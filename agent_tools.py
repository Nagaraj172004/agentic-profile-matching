"""Tools the matching agent can call.

File-system tools come from Milestone 1 (fs_tools.py), rag_search from
Milestone 2 (the Chroma index), and the screening tools from screening.py.
Tools that depend on the current search read the requirements and shortlist
from the graph state through InjectedState, so the model never has to pass
them around.
"""

from __future__ import annotations

import json
from typing import Annotated, List, Optional

from langchain_core.tools import tool
from langgraph.prebuilt import InjectedState

import fs_tools
import screening
from job_matcher import _excerpt, candidate_id
from resume_rag import get_collection, get_model


def _dump(data) -> str:
    return json.dumps(data, indent=1, default=str)


def _requirements(state: dict) -> Optional[dict]:
    return state.get("requirements") if state else None


def _shortlist(state: dict) -> list:
    return (state or {}).get("shortlist") or []


def _resolve_many(refs: List[str], state: dict) -> tuple:
    found, unknown = [], []
    for ref in refs:
        cid = screening.resolve_candidate(ref, _shortlist(state))
        if cid and cid not in found:
            found.append(cid)
        elif not cid:
            unknown.append(ref)
    return found, unknown


# ------------------------------------------------- Milestone 1: file system

@tool
def list_files(directory: str, extension: Optional[str] = None) -> str:
    """List files in a directory (for example 'resumes' or 'jobs'), optionally filtered by extension like .pdf."""
    files = fs_tools.list_files(str(screening.PROJECT_DIR / directory), extension)
    return _dump([{"name": f["name"], "extension": f["extension"], "size_bytes": f["size_bytes"]} for f in files])


@tool
def read_file(filepath: str) -> str:
    """Read a .pdf, .txt, or .docx resume, for example 'resumes/resume_meera_krishnan.txt'."""
    result = fs_tools.read_file(str(screening.PROJECT_DIR / filepath))
    return _dump({k: v for k, v in result.items() if k != "metadata"})


@tool
def search_in_file(filepath: str, keyword: str) -> str:
    """Case-insensitive keyword search in one resume. Returns matching lines with context."""
    return _dump(fs_tools.search_in_file(str(screening.PROJECT_DIR / filepath), keyword))


@tool
def write_file(filepath: str, content: str) -> str:
    """Write text to a file under the project, for example 'reports/notes.md'."""
    return _dump(fs_tools.write_file(str(screening.PROJECT_DIR / filepath), content))


# ---------------------------------------------------- Milestone 2: RAG

@tool
def rag_search(query: str, k: int = 5) -> str:
    """Semantic search over resume sections. Use for open questions such as 'who has payments experience?'."""
    collection = get_collection(screening.CHROMA_DIR)
    payload = collection.query(
        query_embeddings=[get_model().encode(query).tolist()],
        n_results=min(collection.count(), max(1, k) * 5),
        include=["documents", "metadatas", "distances"],
    )
    best = {}
    for document, meta, distance in zip(payload["documents"][0], payload["metadatas"][0], payload["distances"][0]):
        cid = candidate_id(meta["resume_path"])
        similarity = round(1.0 - float(distance), 3)
        if cid not in best or similarity > best[cid]["similarity"]:
            best[cid] = {
                "candidate_id": cid,
                "candidate_name": meta["candidate_name"],
                "similarity": similarity,
                "section": meta["section"],
                "excerpt": _excerpt(document, 200),
                "years": meta["experience_years"],
                "skills": meta["skills"],
            }
    hits = sorted(best.values(), key=lambda h: -h["similarity"])[: max(1, k)]
    return _dump(hits)


# -------------------------------------------------------- screening tools

@tool
def extract_requirements(jd: str) -> str:
    """Parse a job description or request into must-have skills, nice-to-have skills, and minimum years."""
    req = screening.extract_requirements(jd)
    return _dump({k: req[k] for k in ("title", "must_have", "nice_to_have", "min_years", "summary")})


@tool
def compare_candidates(candidate_ids: List[str], state: Annotated[dict, InjectedState]) -> str:
    """Head-to-head comparison of 2-5 candidates against the current requirements.
    Accepts candidate ids, names, first names, or ranks like '#1'."""
    req = _requirements(state)
    if not req:
        return _dump({"error": "No active search. Give a job description first."})
    ids, unknown = _resolve_many(candidate_ids, state)
    if not ids:
        return _dump({"error": "No matching candidates", "unknown": unknown})
    shortlist = {item["candidate_id"]: item for item in _shortlist(state)}
    rows = []
    for cid in ids:
        item = shortlist.get(cid) or screening.round_three(screening.round_two(req, [screening.evaluate_candidate(req, cid)]))[0]
        b = item["breakdown"]
        rows.append(
            {
                "candidate_id": cid,
                "name": item["candidate_name"],
                "rank": item["rank"],
                "score": item["match_score"],
                "score_parts": {
                    "similarity": b["similarity_points"],
                    "skills": b["skill_points"],
                    "years": b["years_points"],
                    "penalty": -b["penalty"],
                },
                "years": b["years"],
                "matched_must_have": b["matched_must"],
                "missing_must_have": b["missing_must"],
                "matched_nice_to_have": b["matched_nice"],
                "recommendation": item["recommendation"],
                "strengths": item["strengths"] + item.get("ai_strengths", []),
                "gaps": item["gaps"] + item.get("ai_concerns", []),
            }
        )
    return _dump({"requirements": {k: req[k] for k in ("must_have", "nice_to_have", "min_years")}, "candidates": rows, "unknown": unknown})


@tool
def explain_ranking(higher_candidate: str, lower_candidate: str, state: Annotated[dict, InjectedState]) -> str:
    """Explain point by point why one candidate ranks above another under the current requirements.
    Use for questions like 'Why did X rank higher than Y?' or 'Why is X not in the list?' (compare with the lowest shortlisted candidate)."""
    req = _requirements(state)
    if not req:
        return _dump({"error": "No active search. Give a job description first."})
    ids, unknown = _resolve_many([higher_candidate, lower_candidate], state)
    if len(ids) < 2:
        return _dump({"error": "Could not identify both candidates", "unknown": unknown})
    return _dump(screening.explain_pair(req, ids[0], ids[1]))


@tool
def generate_interview_questions(candidate_id: str, state: Annotated[dict, InjectedState]) -> str:
    """Create screening interview questions for one candidate, targeting their strengths and gaps."""
    req = _requirements(state)
    if not req:
        return _dump({"error": "No active search. Give a job description first."})
    cid = screening.resolve_candidate(candidate_id, _shortlist(state))
    if not cid:
        return _dump({"error": "Unknown candidate: {0}".format(candidate_id)})
    return _dump(screening.interview_questions(req, cid))


@tool
def get_candidate_report(candidate_id: str, state: Annotated[dict, InjectedState]) -> str:
    """Detailed match report for one candidate: score breakdown, evidence, strengths, gaps, verdict, and improvement suggestions."""
    req = _requirements(state)
    if not req:
        return _dump({"error": "No active search. Give a job description first."})
    cid = screening.resolve_candidate(candidate_id, _shortlist(state))
    if not cid:
        return _dump({"error": "Unknown candidate: {0}".format(candidate_id)})
    shortlist = {item["candidate_id"]: item for item in _shortlist(state)}
    item = shortlist.get(cid) or screening.round_three(screening.round_two(req, [screening.evaluate_candidate(req, cid)]))[0]
    keep = ("candidate_name", "resume_path", "rank", "match_score", "breakdown", "evidence", "strengths", "gaps",
            "ai_strengths", "ai_concerns", "analyst_note", "recommendation", "recommendation_reason", "suggestions")
    return _dump({k: item.get(k) for k in keep})


TOOLS = [
    list_files,
    read_file,
    search_in_file,
    write_file,
    rag_search,
    extract_requirements,
    compare_candidates,
    explain_ranking,
    generate_interview_questions,
    get_candidate_report,
]

TOOLS_BY_NAME = {t.name: t for t in TOOLS}
