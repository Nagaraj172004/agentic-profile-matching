# 1_full_pipeline

## You

jobs/senior_python_backend.txt

<details><summary>Agent reasoning (5 steps)</summary>

- `parse_jd` Parse JD: read job description from jobs/senior_python_backend.txt (341 characters, structured header).
- `extract_requirements` Extract Requirements: must-have Python, Django; nice-to-have PostgreSQL, Docker, REST; minimum 5 years (via rules).
- `search_resumes` Search Resumes (round 1): scored all 100 resumes with hybrid RAG; 14 meet every hard requirement; kept the top 10: Sanjay Kulkarni (91), Hemant Joshi (89), Meera Krishnan (88), Kiran Rao (82), Harish Gupta (80), ...
- `rank_candidates` Rank Candidates (round 2): read 10 resumes in full, found 38 evidence lines, wrote strengths, gaps, and analyst notes (via rules).
- `generate_report` Generate Report (round 3): 9 hire, 1 borderline, 0 no-hire; 0 ranking changes; saved reports/senior_python_backend_engineer_v1.md.

</details>

## Agent

**Senior Python Backend Engineer**: must-have Python, Django; nice-to-have PostgreSQL, Docker, REST; 5+ years.
Screened 100 resumes, kept the top 10, and deep-reviewed them: **9 hire, 1 borderline, 0 no-hire**.

| # | Candidate | Score | Years | Verdict | Main gap |
|---|---|---|---|---|---|
| 1 | Sanjay Kulkarni | 91 | 8 | HIRE | No evidence of nice-to-have: REST |
| 2 | Hemant Joshi | 89 | 7 | HIRE | No evidence of nice-to-have: REST |
| 3 | Meera Krishnan | 88 | 7 | HIRE | No evidence of nice-to-have: REST |
| 4 | Kiran Rao | 82 | 5 | HIRE | No evidence of nice-to-have: PostgreSQL |
| 5 | Harish Gupta | 80 | 11 | HIRE | No evidence of nice-to-have: Docker, REST |
| 6 | Pooja Iyer | 78 | 6 | HIRE | No evidence of nice-to-have: Docker |
| 7 | Arjun Menon | 77 | 6 | HIRE | No evidence of nice-to-have: Docker, REST |
| 8 | Arvind Swamy | 76 | 8 | HIRE | No evidence of nice-to-have: Docker, REST |
| 9 | Imran Sheikh | 75 | 9 | HIRE | No evidence of nice-to-have: Docker, REST |
| 10 | Nagaraj | 72 | 4 | BORDERLINE | 4 years of experience, 1 short of the 5-year minimum |

Full report saved to `reports/senior_python_backend_engineer_v1.md`. Try: "Compare the top 3", "Why did Sanjay rank higher than Hemant?", "How could Nagaraj improve?", "Make <skill> a must-have", "done".

## You

done

<details><summary>Agent reasoning (1 steps)</summary>

- `human_feedback` Human Feedback: "done" -> intent done.

</details>

## Agent

Session finished. Start a new search any time.
