# 2_natural_language_compare

## You

Find me candidates with React and 3+ years experience

<details><summary>Agent reasoning (5 steps)</summary>

- `parse_jd` Parse JD: read job description from the message (53 characters, free text).
- `extract_requirements` Extract Requirements: must-have React; nice-to-have none; minimum 3 years (via llm).
- `search_resumes` Search Resumes (round 1): scored all 100 resumes with hybrid RAG; 10 meet every hard requirement; kept the top 10: Irfan Pathan (78), Fiona Dsilva (78), Rhea Banerjee (71), Sneha Kulkarni (69), Ishaan Kapoor (67), ...
- `rank_candidates` Rank Candidates (round 2): read 10 resumes in full, found 10 evidence lines, wrote strengths, gaps, and analyst notes (via LLM).
- `generate_report` Generate Report (round 3): 5 hire, 5 borderline, 0 no-hire; 0 ranking changes; saved reports/react_developer_v1.md.

</details>

## Agent

**React Developer**: must-have React; nice-to-have none; 3+ years.
Screened 100 resumes, kept the top 10, and deep-reviewed them: **5 hire, 5 borderline, 0 no-hire**.

| # | Candidate | Score | Years | Verdict | Main gap |
|---|---|---|---|---|---|
| 1 | Irfan Pathan | 78 | 5 | HIRE | - |
| 2 | Fiona Dsilva | 78 | 7 | HIRE | - |
| 3 | Rhea Banerjee | 71 | 5 | HIRE | - |
| 4 | Sneha Kulkarni | 69 | 6 | HIRE | - |
| 5 | Ishaan Kapoor | 67 | 3 | HIRE | - |
| 6 | Lavanya Suresh | 64 | 8 | BORDERLINE | fit score below the hire bar of 65 |
| 7 | Keshav Murthy | 61 | 4 | BORDERLINE | fit score below the hire bar of 65 |
| 8 | Jatin Kohli | 60 | 3 | BORDERLINE | fit score below the hire bar of 65 |
| 9 | Elango Ramesh | 59 | 4 | BORDERLINE | fit score below the hire bar of 65 |
| 10 | Divya Sharma | 59 | 4 | BORDERLINE | fit score below the hire bar of 65 |

**Agent's take:** Interview Irfan Pathan first because he has the highest score among the top candidates and a solid full‑stack React background, making him a low‑risk hire. He is a strong hire candidate with no gaps, so he can be onboarded quickly. The most promising borderline candidate is Lavanya Suresh, whose main gap is none.

Full report saved to `reports/react_developer_v1.md`. Try: "Compare the top 3", "Why did Irfan rank higher than Fiona?", "How could Lavanya Suresh improve?", "Make <skill> a must-have", "done".

## You

Compare the top 3 matches side by side

<details><summary>Agent reasoning (4 steps)</summary>

- `human_feedback` Human Feedback: "Compare the top 3 matches side by side" -> intent compare.
- `agent` Agent: calling compare_candidates({"candidate_ids": ["#1", "#2", "#3"]}).
- `tools` compare_candidates -> { "requirements": { "must_have": [ "React" ], "nice_to_have": [], "min_years": 3 }, "candidates": [ { "candidate_id": "irfan_pathan", "name": "Irfan Pathan", "rank": 1, "score": 78, "score_parts": { "similarity": 38.2, "skills": 25.0, "years": 15.0, "penalty": -0.0 }, "years": 5, "matched_must_have"
- `agent` Agent: answered after 1 tool round(s).

</details>

## Agent

**Side‑by‑side comparison of the top 3 React candidates**

| Feature | **Irfan Pathan** | **Fiona Dsilva** | **Rhea Banerjee** |
|---------|------------------|------------------|-------------------|
| **Rank** | 1 | 2 | 3 |
| **Score** | 78 | 78 | 71 |
| **Score parts** | similarity 38.2 | skills 25 | years 15 | similarity 38.0 | skills 25 | years 15 | similarity 30.8 | skills 25 | years 15 |
| **Years of React experience** | 5 | 7 | 5 |
| **Must‑have matched** | React | React | React |
| **Nice‑to‑have matched** | – | – | – |
| **Strengths** | • 5 yrs React + TS<br>• Full‑stack (Node.js, PostgreSQL)<br>• 67 % resume similarity<br>• Consistent end‑to‑end delivery | • 7 yrs React + TS<br>• Led Next.js migration<br>• 67 % similarity<br>• GraphQL & Jest | • 5 yrs React + TS<br>• Migrated dashboard to React/TS<br>• 62 % similarity<br>• GraphQL & Node.js |
| **Gaps** | • No testing frameworks<br>• No performance tuning<br>• No UI/UX design system mention | • No bundle optimization<br>• No Redux<br>• Limited accessibility detail | • No automated testing<br>• No bundle optimization<br>• No design system mention |
| **Verdict** | HIRE | HIRE | HIRE |

**Takeaway**  
All three meet the must‑have React skill and 3+ years requirement.  
Irfan and Fiona tie on score; Fiona has a higher years count (7 vs 5) but similar similarity.  
Rhea’s score is lower mainly due to a 30.8 % similarity, but still above the hire threshold.  
All are strong hires; prioritize based on other factors (e.g., specific tech stack fit, team culture).
