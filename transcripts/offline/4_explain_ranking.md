# 4_explain_ranking

## You

jobs/data_engineer.txt

<details><summary>Agent reasoning (5 steps)</summary>

- `parse_jd` Parse JD: read job description from jobs/data_engineer.txt (304 characters, structured header).
- `extract_requirements` Extract Requirements: must-have Python, Spark, SQL; nice-to-have Airflow; minimum 3 years (via rules).
- `search_resumes` Search Resumes (round 1): scored all 100 resumes with hybrid RAG; 9 meet every hard requirement; kept the top 10: Rahul Iyer (88), Chetan Bhat (86), Aisha Khan (86), Waseem Akram (86), Zubin Mistry (79), ...
- `rank_candidates` Rank Candidates (round 2): read 10 resumes in full, found 34 evidence lines, wrote strengths, gaps, and analyst notes (via rules).
- `generate_report` Generate Report (round 3): 8 hire, 1 borderline, 1 no-hire; 0 ranking changes; saved reports/data_engineer_v1.md.

</details>

## Agent

**Data Engineer**: must-have Python, Spark, SQL; nice-to-have Airflow; 3+ years.
Screened 100 resumes, kept the top 10, and deep-reviewed them: **8 hire, 1 borderline, 1 no-hire**.

| # | Candidate | Score | Years | Verdict | Main gap |
|---|---|---|---|---|---|
| 1 | Rahul Iyer | 88 | 6 | HIRE | - |
| 2 | Chetan Bhat | 86 | 6 | HIRE | No evidence of nice-to-have: Airflow |
| 3 | Aisha Khan | 86 | 7 | HIRE | - |
| 4 | Waseem Akram | 86 | 5 | HIRE | - |
| 5 | Zubin Mistry | 79 | 9 | HIRE | No evidence of nice-to-have: Airflow |
| 6 | Tarun Malhotra | 78 | 3 | HIRE | No evidence of nice-to-have: Airflow |
| 7 | Neelam Choudhary | 74 | 5 | HIRE | - |
| 8 | Joseph Mathew | 67 | 4 | HIRE | No evidence of nice-to-have: Airflow |
| 9 | Deepika Rawat | 64 | 3 | BORDERLINE | fit score below the hire bar of 65 |
| 10 | Yamini Krishna | 45 | 2 | NO-HIRE | Missing must-have skill: Spark |

Full report saved to `reports/data_engineer_v1.md`. Try: "Compare the top 3", "Why did Rahul rank higher than Chetan?", "How could Deepika Rawat improve?", "Make <skill> a must-have", "done".

## You

Why did Rahul Iyer rank higher than Chetan Bhat?

<details><summary>Agent reasoning (2 steps)</summary>

- `human_feedback` Human Feedback: "Why did Rahul Iyer rank higher than Chetan Bhat?" -> intent explain.
- `agent` Agent: LLM unavailable, answered with rule-based tools.

</details>

## Agent

**Rahul Iyer** (#1, score 88) ranks above **Chetan Bhat** (#2, score 86) by 2 points.
- skill coverage: 25.0 vs 18.8 (+6.2)
- semantic similarity: 48.2 vs 51.9 (-3.7)
- Only Rahul Iyer lists: Airflow
Rule: score = 60 x calibrated similarity + 25 x share of job skills + 15 x years ratio, minus 15 per missing must-have, minus 10 plus 5 per missing year when below the years bar

## You

Why is Yamini Krishna not a hire? What are the gaps?

<details><summary>Agent reasoning (2 steps)</summary>

- `human_feedback` Human Feedback: "Why is Yamini Krishna not a hire? What are the gaps?" -> intent explain.
- `agent` Agent: LLM unavailable, answered with rule-based tools.

</details>

## Agent

**Yamini Krishna**: #10, score 45, verdict no-hire. 2 hard-requirement gaps and a score of 45.
Strengths:
- Has must-haves: Python, SQL
- Brings nice-to-have skills: Airflow
- Resume wording closely matches the role (72% similarity)
Gaps:
- Missing must-have skill: Spark
- 2 years of experience, 1 short of the 3-year minimum
Improvement suggestions:
- Show hands-on Spark (a shipped project, open-source work, or certification); it is a must-have.
- Has 2 of 3 required years; consider for a mid-level opening, or revisit after 1 year more.
