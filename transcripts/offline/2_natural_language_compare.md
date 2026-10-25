# 2_natural_language_compare

## You

Find me candidates with React and 3+ years experience

<details><summary>Agent reasoning (5 steps)</summary>

- `parse_jd` Parse JD: read job description from the message (53 characters, free text).
- `extract_requirements` Extract Requirements: must-have React; nice-to-have none; minimum 3 years (via rules).
- `search_resumes` Search Resumes (round 1): scored all 100 resumes with hybrid RAG; 10 meet every hard requirement; kept the top 10: Fiona Dsilva (72), Irfan Pathan (64), Sneha Kulkarni (64), Rhea Banerjee (64), Ishaan Kapoor (60), ...
- `rank_candidates` Rank Candidates (round 2): read 10 resumes in full, found 10 evidence lines, wrote strengths, gaps, and analyst notes (via rules).
- `generate_report` Generate Report (round 3): 1 hire, 9 borderline, 0 no-hire; 0 ranking changes; saved reports/candidates_with_react_v1.md.

</details>

## Agent

**Candidates with React**: must-have React; nice-to-have none; 3+ years.
Screened 100 resumes, kept the top 10, and deep-reviewed them: **1 hire, 9 borderline, 0 no-hire**.

| # | Candidate | Score | Years | Verdict | Main gap |
|---|---|---|---|---|---|
| 1 | Fiona Dsilva | 72 | 7 | HIRE | - |
| 2 | Irfan Pathan | 64 | 5 | BORDERLINE | fit score below the hire bar of 65 |
| 3 | Sneha Kulkarni | 64 | 6 | BORDERLINE | fit score below the hire bar of 65 |
| 4 | Rhea Banerjee | 64 | 5 | BORDERLINE | fit score below the hire bar of 65 |
| 5 | Ishaan Kapoor | 60 | 3 | BORDERLINE | fit score below the hire bar of 65 |
| 6 | Lavanya Suresh | 56 | 8 | BORDERLINE | fit score below the hire bar of 65 |
| 7 | Elango Ramesh | 53 | 4 | BORDERLINE | fit score below the hire bar of 65 |
| 8 | Divya Sharma | 50 | 4 | BORDERLINE | fit score below the hire bar of 65 |
| 9 | Gopal Krishnan | 49 | 1 | BORDERLINE | 1 year of experience, 2 short of the 3-year minimum |
| 10 | Keshav Murthy | 48 | 4 | BORDERLINE | fit score below the hire bar of 65 |

Full report saved to `reports/candidates_with_react_v1.md`. Try: "Compare the top 3", "Why did Fiona rank higher than Irfan?", "How could Irfan Pathan improve?", "Make <skill> a must-have", "done".

## You

Compare the top 3 matches side by side

<details><summary>Agent reasoning (2 steps)</summary>

- `human_feedback` Human Feedback: "Compare the top 3 matches side by side" -> intent compare.
- `agent` Agent: LLM unavailable, answered with rule-based tools.

</details>

## Agent

| Candidate | Rank | Score | Similarity | Skills | Years | Penalty | Missing must-haves | Verdict |
|---|---|---|---|---|---|---|---|---|
| Fiona Dsilva | 1 | 72 | 32.0 | 25.0 | 7y (15.0) | -0.0 | - | hire |
| Irfan Pathan | 2 | 64 | 24.4 | 25.0 | 5y (15.0) | -0.0 | - | borderline |
| Sneha Kulkarni | 3 | 64 | 24.4 | 25.0 | 6y (15.0) | -0.0 | - | borderline |
