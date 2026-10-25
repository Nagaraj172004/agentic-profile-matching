"""LangGraph candidate-matching agent.

START -> parse_jd -> extract_requirements -> search_resumes -> rank_candidates
      -> generate_report -> human_feedback -> (refine | new search | tool agent | END)

search_resumes, rank_candidates, and generate_report are the three screening
rounds: score all resumes and keep 10, deep-read those 10, then give each a
hire / borderline / no-hire verdict. human_feedback pauses the graph with
interrupt() and routes the recruiter's next message. Requirement changes go
back through the pipeline and the new report explains what moved; questions
go to a tool-calling agent that loops through ToolNode and returns to
human_feedback.
"""

from __future__ import annotations

import json
import operator
import re
import uuid
from typing import Annotated, Callable, List, Literal, Optional, TypedDict

from langchain_core.messages import AIMessage, AnyMessage, HumanMessage, SystemMessage, ToolMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langgraph.types import Command, interrupt
from pydantic import BaseModel, Field

import llm
import screening
from agent_tools import TOOLS
from fs_tools import write_file

SHORTLIST_SIZE = 10
MAX_TOOL_ROUNDS = 4
INTENTS = ("refine", "new_search", "compare", "explain", "questions", "candidate_detail", "chat", "done")
INTENT_TOOL = {
    "compare": "compare_candidates",
    "explain": "explain_ranking",
    "questions": "generate_interview_questions",
}


class MatchState(TypedDict, total=False):
    messages: Annotated[List[AnyMessage], add_messages]
    trace: Annotated[List[str], operator.add]
    jd_text: str
    requirements: dict
    requirement_history: list
    change_summary: str
    pool_size: int
    qualified: int
    round1: list
    shortlist: list
    previous_shortlist: list
    previous_requirements: dict
    ranking_changes: list
    report_path: str
    report_version: int
    intent: str
    turn_start: int


# ------------------------------------------------------------- helpers

def _last_human(state: MatchState) -> str:
    for message in reversed(state.get("messages", [])):
        if isinstance(message, HumanMessage):
            return str(message.content)
    return ""


def _names(items: list, limit: int = 5) -> str:
    return ", ".join("{0} ({1})".format(i["candidate_name"], i["match_score"]) for i in items[:limit])


def shortlist_context(state: MatchState) -> str:
    req = state.get("requirements")
    if not req:
        return "No search has been run yet."
    lines = [
        "Current role: {0}".format(req["title"]),
        "Must-have: {0}. Nice-to-have: {1}. Minimum years: {2}.".format(
            ", ".join(req["must_have"]) or "none", ", ".join(req["nice_to_have"]) or "none", req["min_years"]),
        "Screened {0} resumes; shortlist (rank, id, name, score, verdict, missing must-haves, years):".format(state.get("pool_size", "?")),
    ]
    for item in state.get("shortlist", []):
        b = item["breakdown"]
        lines.append("#{0} {1} | {2} | {3} | {4} | missing: {5} | {6}y".format(
            item["rank"], item["candidate_id"], item["candidate_name"], item["match_score"],
            item.get("recommendation", "?"), ", ".join(b["missing_must"]) or "-", b["years"]))
    return "\n".join(lines)


# ------------------------------------------------------- pipeline nodes

def parse_jd(state: MatchState) -> dict:
    raw = (state.get("jd_text") or "").strip()
    source = "the message"
    match = re.search(r"jobs[/\\][\w.-]+\.txt", raw)
    if match and (screening.PROJECT_DIR / match.group(0)).is_file():
        source = match.group(0).replace("\\", "/")
        raw = (screening.PROJECT_DIR / match.group(0)).read_text(encoding="utf-8").strip()
    kind = "structured header" if "Must-have skills:" in raw else "free text"
    return {
        "jd_text": raw,
        "intent": "new_search",
        "previous_shortlist": [],
        "previous_requirements": {},
        "ranking_changes": [],
        "report_version": 0,
        "trace": ["Parse JD: read job description from {0} ({1} characters, {2}).".format(source, len(raw), kind)],
    }


def extract_requirements_node(state: MatchState) -> dict:
    current = state.get("requirements")
    if state.get("intent") == "refine" and current:
        instruction = _last_human(state)
        new = screening.refine_requirements(current, instruction)
        changes = screening.describe_requirement_change(current, new)
        summary = "; ".join(changes) if changes else "no change to the requirements"
        return {
            "requirements": new,
            "requirement_history": state.get("requirement_history", []) + [new],
            "previous_shortlist": state.get("shortlist", []),
            "previous_requirements": current,
            "change_summary": summary,
            "trace": ["Extract Requirements: applied \"{0}\" -> {1} (via {2}).".format(instruction, summary, new["source"])],
        }
    new = screening.extract_requirements(state.get("jd_text", ""))
    return {
        "requirements": new,
        "requirement_history": [new],
        "previous_shortlist": [],
        "previous_requirements": {},
        "change_summary": "",
        "trace": ["Extract Requirements: must-have {0}; nice-to-have {1}; minimum {2} years (via {3}).".format(
            ", ".join(new["must_have"]) or "none", ", ".join(new["nice_to_have"]) or "none", new["min_years"], new["source"])],
    }


def search_resumes(state: MatchState) -> dict:
    result = screening.round_one(state["requirements"], k=SHORTLIST_SIZE)
    return {
        "pool_size": result["pool_size"],
        "qualified": result["qualified"],
        "round1": result["top"],
        "trace": ["Search Resumes (round 1): scored all {0} resumes with hybrid RAG; {1} meet every hard requirement; kept the top {2}: {3}, ...".format(
            result["pool_size"], result["qualified"], len(result["top"]), _names(result["top"]))],
    }


def rank_candidates(state: MatchState) -> dict:
    analysed = screening.round_two(state["requirements"], state.get("round1", []))
    evidence = sum(len(item.get("evidence", {})) for item in analysed)
    source = "LLM" if any(item.get("ai_strengths") for item in analysed) else "rules"
    return {
        "shortlist": analysed,
        "trace": ["Rank Candidates (round 2): read {0} resumes in full, found {1} evidence lines, wrote strengths, gaps, and analyst notes (via {2}).".format(
            len(analysed), evidence, source)],
    }


AGENT_TAKE_PROMPT = """You are a recruiting lead. In 2-3 sentences, say who to interview first and why.
Then name the most promising candidate from borderline_candidates and their main gap; if that list is empty, say there are no borderline cases.
Use only the data given and keep each candidate's verdict exactly as given. Plain text, no lists."""


def generate_report(state: MatchState) -> dict:
    req = state["requirements"]
    final = screening.round_three(state.get("shortlist", []))
    previous = state.get("previous_shortlist") or []
    changes = []
    if previous and state.get("previous_requirements"):
        changes = screening.diff_rankings(state["previous_requirements"], req, previous, final)
    version = int(state.get("report_version") or 0) + 1
    report = screening.render_report(req, final, state.get("pool_size", 0), state.get("qualified", 0), changes, version)
    path = "reports/{0}_v{1}.md".format(screening.slug(req["title"]), version)
    write_file(str(screening.PROJECT_DIR / path), report)

    counts = {verdict: sum(1 for i in final if i["recommendation"] == verdict) for verdict in ("hire", "borderline", "no-hire")}
    lines = [
        "**{0}**: must-have {1}; nice-to-have {2}; {3}+ years.".format(
            req["title"], ", ".join(req["must_have"]) or "none", ", ".join(req["nice_to_have"]) or "none", req["min_years"]),
        "Screened {0} resumes, kept the top {1}, and deep-reviewed them: **{2} hire, {3} borderline, {4} no-hire**.".format(
            state.get("pool_size", 0), len(final), counts["hire"], counts["borderline"], counts["no-hire"]),
        "",
    ]
    if state.get("change_summary"):
        lines.append("**Requirement change:** {0}.".format(state["change_summary"]))
        if changes:
            lines.append("")
            lines.append("**How the ranking moved:**")
            for change in changes[:8]:
                lines.append("- {0} {1} (score {2} -> {3}): {4}".format(
                    change["candidate_name"], change["movement"], change["old_score"], change["new_score"], "; ".join(change["reasons"])))
        else:
            lines.append("The top {0} did not change.".format(len(final)))
        lines.append("")
    lines += ["| # | Candidate | Score | Years | Verdict | Main gap |", "|---|---|---|---|---|---|"]
    for item in final:
        hard_gaps = [g for g in item["gaps"] if not g.startswith("No evidence of nice-to-have")]
        if hard_gaps:
            gap = hard_gaps[0]
        elif item["recommendation"] != "hire":
            gap = "fit score below the hire bar of {0}".format(screening.HIRE_SCORE)
        else:
            gap = item["gaps"][0] if item["gaps"] else "-"
        lines.append("| {0} | {1} | {2} | {3} | {4} | {5} |".format(
            item["rank"], item["candidate_name"], item["match_score"], item["breakdown"]["years"],
            screening.VERDICT_LABEL[item["recommendation"]], gap))
    lines.append("")

    compact = [
        {"name": i["candidate_name"], "score": i["match_score"], "verdict": i["recommendation"],
         "gaps": i["gaps"][:2], "note": i.get("analyst_note", "")}
        for i in final[:6]
    ]
    borderline_info = [
        {"name": i["candidate_name"], "score": i["match_score"], "gaps": i["gaps"][:2]}
        for i in final if i["recommendation"] == "borderline"
    ]
    take = llm.text(
        [("system", AGENT_TAKE_PROMPT), ("human", json.dumps(
            {"role": req["title"], "top_candidates": compact, "borderline_candidates": borderline_info}))],
        where="agent take",
    )
    if take:
        lines += ["**Agent's take:** {0}".format(take), ""]
    borderline = next((i["candidate_name"] for i in final if i["recommendation"] == "borderline"), None)
    top = [i["candidate_name"].split()[0] for i in final[:2]]
    examples = ["\"Compare the top 3\""]
    if len(top) == 2:
        examples.append("\"Why did {0} rank higher than {1}?\"".format(top[0], top[1]))
    if borderline:
        examples.append("\"How could {0} improve?\"".format(borderline))
    examples += ["\"Make <skill> a must-have\"", "\"done\""]
    lines.append("Full report saved to `{0}`. Try: {1}.".format(path, ", ".join(examples)))
    return {
        "shortlist": final,
        "ranking_changes": changes,
        "report_path": path,
        "report_version": version,
        "messages": [AIMessage(content="\n".join(lines))],
        "trace": ["Generate Report (round 3): {0} hire, {1} borderline, {2} no-hire; {3} ranking changes; saved {4}.".format(
            counts["hire"], counts["borderline"], counts["no-hire"], len(changes), path)],
    }


# ------------------------------------------------- human-in-the-loop node

class Route(BaseModel):
    intent: Literal["refine", "new_search", "compare", "explain", "questions", "candidate_detail", "chat", "done"]
    reason: str = Field(description="Short reason for the choice")


ROUTER_PROMPT = """You route a recruiter's message inside a candidate-matching assistant.
{context}

Intents:
- refine: change the CURRENT requirements so candidates are re-ranked (require or drop a skill, make a skill nice-to-have, change minimum years, "also need X", "what if we drop Y").
- new_search: a different role or a fresh request ("Find me candidates with ...", a pasted job description, a jobs/*.txt path).
- compare: compare two or more candidates side by side.
- explain: why one candidate ranked above or below another, or why someone is or is not on the list.
- questions: interview or screening questions for a candidate.
- candidate_detail: strengths, gaps, evidence, verdict, or improvement suggestions for one candidate.
- chat: anything else, such as questions about the data or open searches like "who has Kafka experience?".
- done: the recruiter wants to finish."""


def rule_based_intent(text: str, has_search: bool) -> str:
    t = text.lower().strip()
    if re.fullmatch(r"(done|quit|exit|bye|stop|end|that'?s all|thanks?,? that'?s all)[.!]?", t):
        return "done"
    if re.search(r"jobs[/\\][\w.-]+\.txt", t) or re.match(r"(find|search|look for|show)( me)? (candidates|people|engineers|developers|someone)", t) or len(t) > 300:
        return "new_search"
    if not has_search:
        return "new_search"
    if re.search(r"interview|screening question|questions for", t):
        return "questions"
    if re.search(r"compare|side by side|side-by-side|\bvs\.?\b|versus|head to head", t):
        return "compare"
    if re.search(r"\bwhy\b|rank(ed)? (higher|lower|above|below)|explain", t):
        return "explain"
    if re.search(r"must[- ]have|nice[- ]to[- ]have|\brequire|\bdrop\b|\bremove\b|\bmin(imum)?\b|\d+\s*\+?\s*years|also need|instead of|optional", t):
        return "refine"
    if re.search(r"strength|gap|improve|suggest|report on|tell me about|hire|recommend", t):
        return "candidate_detail"
    return "chat"


def classify_intent(text: str, state: MatchState) -> str:
    has_search = bool(state.get("requirements"))
    quick = rule_based_intent(text, has_search)
    if quick == "done" or not has_search:
        return quick
    result = llm.structured(
        Route,
        [("system", ROUTER_PROMPT.format(context=shortlist_context(state))), ("human", text)],
        where="intent router",
    )
    return result.intent if result is not None else quick


def human_feedback(state: MatchState) -> dict:
    reply = interrupt({"prompt": "Ask a question, change the requirements, or type 'done'.", "report_path": state.get("report_path")})
    text = str(reply).strip()
    intent = classify_intent(text, state)
    update = {
        "messages": [HumanMessage(content=text)],
        "intent": intent,
        "turn_start": len(state.get("messages", [])),
        "trace": ["Human Feedback: \"{0}\" -> intent {1}.".format(text[:120], intent)],
    }
    if intent == "new_search":
        update["jd_text"] = text
    return update


def route_feedback(state: MatchState) -> str:
    intent = state.get("intent")
    if intent == "done":
        return END
    if intent == "refine":
        return "extract_requirements"
    if intent == "new_search":
        return "parse_jd"
    return "agent"


# --------------------------------------------------- tool-calling agent

AGENT_PROMPT = """You are a recruiting assistant that explains candidate rankings and screening results.
{context}

The latest message was classified as: {intent}.
Rules:
- Ground every claim in tool results or the shortlist above. Never invent candidates, skills, years, or scores.
- compare_candidates for side-by-side comparisons, explain_ranking for "why X above Y" or "why isn't X listed", generate_interview_questions for screening questions, get_candidate_report for one candidate's strengths, gaps, or improvement suggestions, rag_search for open questions about skills or experience, and the file tools to read resumes.
- For any question about one candidate (why they are or are not a hire, their gaps, how they could improve), call get_candidate_report first. The shortlist above has no score breakdown, so do not guess points from it.
- Tools accept candidate ids, full names, first names, or ranks such as "#2".
- When explaining rankings, cite the score parts (similarity, skills, years, penalty) and the concrete skills or years that differ.
- Answer in concise markdown. Use a table for side-by-side comparisons.
- If the user wants different requirements, tell them to say it directly (for example "make Docker a must-have") so the pipeline re-ranks."""


def _recent_history(state: MatchState, limit: int = 6) -> list:
    start = state.get("turn_start", len(state.get("messages", [])))
    earlier = []
    for message in state.get("messages", [])[:start]:
        if isinstance(message, HumanMessage):
            earlier.append(HumanMessage(content=str(message.content)[:1500]))
        elif isinstance(message, AIMessage) and not message.tool_calls and message.content:
            earlier.append(AIMessage(content=str(message.content)[:1500]))
    return earlier[-limit:]


def agent(state: MatchState) -> dict:
    turn = state.get("messages", [])[state.get("turn_start", 0):]
    tool_rounds = sum(1 for m in turn if isinstance(m, AIMessage) and m.tool_calls)
    model = llm.get_llm()
    if model is None:
        return {"messages": [AIMessage(content=fallback_answer(state))], "trace": ["Agent: LLM unavailable, answered with rule-based tools."]}

    prompt = AGENT_PROMPT.format(context=shortlist_context(state), intent=state.get("intent", "chat"))
    messages = [SystemMessage(content=prompt)] + _recent_history(state) + list(turn)
    forced = INTENT_TOOL.get(state.get("intent")) if tool_rounds == 0 else None
    response = None
    attempts = []
    if tool_rounds >= MAX_TOOL_ROUNDS:
        attempts.append(("final answer", lambda: model.invoke(messages)))
    else:
        if forced:
            attempts.append(("forced " + forced, lambda: model.bind_tools(TOOLS, tool_choice=forced).invoke(messages)))
        attempts.append(("auto tool choice", lambda: model.bind_tools(TOOLS).invoke(messages)))
    notes = []
    for label, attempt in attempts:
        try:
            response = llm.call(attempt, "agent " + label)
            break
        except Exception as exc:
            notes.append("Agent: {0} failed ({1}); retrying.".format(label, str(exc)[:120]))
            if "429" in str(exc):
                break
    if response is None:
        return {"messages": [AIMessage(content=fallback_answer(state))], "trace": notes + ["Agent: model call failed, answered with rule-based tools."]}

    if response.tool_calls:
        calls = ", ".join("{0}({1})".format(c["name"], json.dumps(c["args"])[:120]) for c in response.tool_calls)
        trace = "Agent: calling {0}.".format(calls)
    else:
        trace = "Agent: answered after {0} tool round(s).".format(tool_rounds)
    return {"messages": [response], "trace": notes + [trace]}


def route_agent(state: MatchState) -> str:
    last = state["messages"][-1]
    if isinstance(last, AIMessage) and last.tool_calls:
        return "tools"
    return "human_feedback"


# ------------------------------------------- rule-based answers (no LLM)

def mentioned_candidates(text: str, state: MatchState) -> list:
    """Candidate ids named in text, in order, plus 'top N' and '#N' references."""
    shortlist = state.get("shortlist", [])
    lowered = text.lower()
    hits = []
    for cid, name in screening.all_candidates():
        parts = name.lower().split()
        for probe in [name.lower()] + parts[:1]:
            index = re.search(r"(?<!\w)" + re.escape(probe) + r"(?!\w)", lowered)
            if index:
                hits.append((index.start(), cid))
                break
    in_list = {i["candidate_id"] for i in shortlist}
    hits.sort(key=lambda pair: (pair[0], pair[1] not in in_list))
    ordered = []
    for _pos, cid in hits:
        if cid not in ordered:
            ordered.append(cid)
    for match in re.finditer(r"#(\d{1,2})", text):
        position = int(match.group(1))
        if 1 <= position <= len(shortlist) and shortlist[position - 1]["candidate_id"] not in ordered:
            ordered.append(shortlist[position - 1]["candidate_id"])
    top = re.search(r"top\s*(\d{1,2})", lowered)
    if top and not ordered:
        ordered = [i["candidate_id"] for i in shortlist[: int(top.group(1))]]
    return ordered


def fallback_answer(state: MatchState) -> str:
    text = _last_human(state)
    intent = state.get("intent", "chat")
    req = state.get("requirements")
    ids = mentioned_candidates(text, state)
    shortlist = state.get("shortlist", [])
    if not req:
        return "Start by giving me a job description or a request such as 'Find me candidates with React and 3+ years'."
    if intent == "compare":
        ids = ids or [i["candidate_id"] for i in shortlist[:3]]
        rows = ["| Candidate | Rank | Score | Similarity | Skills | Years | Penalty | Missing must-haves | Verdict |", "|---|---|---|---|---|---|---|---|---|"]
        for cid in ids[:5]:
            item = next((i for i in shortlist if i["candidate_id"] == cid), None) or screening.round_three([screening.evaluate_candidate(req, cid)])[0]
            b = item["breakdown"]
            rows.append("| {0} | {1} | {2} | {3} | {4} | {5}y ({6}) | -{7} | {8} | {9} |".format(
                item["candidate_name"], item["rank"], item["match_score"], b["similarity_points"], b["skill_points"],
                b["years"], b["years_points"], b["penalty"], ", ".join(b["missing_must"]) or "-", item["recommendation"]))
        return "\n".join(rows)
    if intent == "explain" and len(ids) == 1:
        intent = "candidate_detail"
    if intent == "explain":
        if len(ids) < 2:
            ids = ids + [i["candidate_id"] for i in shortlist if i["candidate_id"] not in ids][: 2 - len(ids)]
        result = screening.explain_pair(req, ids[0], ids[1])
        if "error" in result:
            return result["error"]
        lines = ["**{0}** (#{1}, score {2}) ranks above **{3}** (#{4}, score {5}) by {6} points.".format(
            result["higher"]["name"], result["higher"]["rank"], result["higher"]["score"],
            result["lower"]["name"], result["lower"]["rank"], result["lower"]["score"], result["score_gap"])]
        for factor in result["factors"]:
            lines.append("- {0}: {1} vs {2} ({3:+})".format(factor["factor"], factor["higher"], factor["lower"], factor["difference"]))
        if result["only_higher_has"]:
            lines.append("- Only {0} lists: {1}".format(result["higher"]["name"], ", ".join(result["only_higher_has"])))
        if result["only_lower_has"]:
            lines.append("- Only {0} lists: {1}".format(result["lower"]["name"], ", ".join(result["only_lower_has"])))
        lines.append("Rule: " + result["scoring_rule"])
        return "\n".join(lines)
    if intent == "questions":
        cid = (ids or [i["candidate_id"] for i in shortlist if i["recommendation"] == "borderline"] or [shortlist[0]["candidate_id"]])[0]
        result = screening.interview_questions(req, cid)
        return "Screening questions for **{0}**:\n".format(result["candidate_name"]) + "\n".join(
            "{0}. {1}".format(n, q) for n, q in enumerate(result["questions"], start=1))
    if intent == "candidate_detail" and ids:
        item = next((i for i in shortlist if i["candidate_id"] == ids[0]), None) or screening.round_three(
            screening.round_two(req, [screening.evaluate_candidate(req, ids[0])]))[0]
        parts = ["**{0}**: #{1}, score {2}, verdict {3}. {4}".format(
            item["candidate_name"], item["rank"], item["match_score"], item["recommendation"], item["recommendation_reason"])]
        parts += ["Strengths:"] + ["- " + s for s in item["strengths"]]
        parts += ["Gaps:"] + (["- " + g for g in item["gaps"]] or ["- none"])
        tips = screening.improvement_suggestions(item)
        if tips:
            parts += ["Improvement suggestions:"] + ["- " + t for t in tips]
        return "\n".join(parts)
    return shortlist_context(state)


# ---------------------------------------------------------------- graph

def build_graph(checkpointer=None):
    graph = StateGraph(MatchState)
    graph.add_node("parse_jd", parse_jd)
    graph.add_node("extract_requirements", extract_requirements_node)
    graph.add_node("search_resumes", search_resumes)
    graph.add_node("rank_candidates", rank_candidates)
    graph.add_node("generate_report", generate_report)
    graph.add_node("human_feedback", human_feedback)
    graph.add_node("agent", agent)
    graph.add_node("tools", ToolNode(TOOLS))

    graph.add_edge(START, "parse_jd")
    graph.add_edge("parse_jd", "extract_requirements")
    graph.add_edge("extract_requirements", "search_resumes")
    graph.add_edge("search_resumes", "rank_candidates")
    graph.add_edge("rank_candidates", "generate_report")
    graph.add_edge("generate_report", "human_feedback")
    graph.add_conditional_edges(
        "human_feedback",
        route_feedback,
        {"extract_requirements": "extract_requirements", "parse_jd": "parse_jd", "agent": "agent", END: END},
    )
    graph.add_conditional_edges("agent", route_agent, {"tools": "tools", "human_feedback": "human_feedback"})
    graph.add_edge("tools", "agent")
    return graph.compile(checkpointer=checkpointer or MemorySaver())


class MatchingSession:
    """One conversation: the first message starts a search, later ones resume the interrupt."""

    def __init__(self, thread_id: Optional[str] = None):
        self.graph = build_graph()
        self.config = {"configurable": {"thread_id": thread_id or uuid.uuid4().hex}, "recursion_limit": 60}
        self.started = False

    @property
    def state(self) -> dict:
        return self.graph.get_state(self.config).values

    @property
    def finished(self) -> bool:
        return self.started and not self.graph.get_state(self.config).next

    def send(self, text: str, on_event: Optional[Callable[[dict], None]] = None) -> List[dict]:
        """Run the graph until it pauses for input or ends. Returns trace, tool, and answer events."""
        if self.finished:
            self.graph = build_graph()
            self.config["configurable"]["thread_id"] = uuid.uuid4().hex
            self.started = False
        if not self.started:
            payload = {"jd_text": text, "messages": [HumanMessage(content=text)]}
            self.started = True
        else:
            payload = Command(resume=text)
        events = []

        def emit(kind: str, node: str, body: str) -> None:
            event = {"kind": kind, "node": node, "text": body}
            events.append(event)
            if on_event:
                on_event(event)

        for chunk in self.graph.stream(payload, self.config, stream_mode="updates"):
            for node, update in chunk.items():
                if node == "__interrupt__" or not isinstance(update, dict):
                    continue
                for line in update.get("trace", []):
                    emit("trace", node, line)
                for message in update.get("messages", []):
                    if isinstance(message, ToolMessage):
                        emit("tool_result", node, "{0} -> {1}".format(message.name, " ".join(str(message.content).split())[:300]))
                    elif isinstance(message, AIMessage) and not message.tool_calls and message.content:
                        emit("answer", node, str(message.content))
        if self.finished:
            emit("answer", "END", "Session finished. Start a new search any time.")
        return events
