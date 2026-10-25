# 1_full_pipeline

## You

jobs/senior_python_backend.txt

<details><summary>Agent reasoning (5 steps)</summary>

- `parse_jd` Parse JD: read job description from jobs/senior_python_backend.txt (341 characters, structured header).
- `extract_requirements` Extract Requirements: must-have Python, Django; nice-to-have Docker, query tuning; minimum 5 years (via llm).
- `search_resumes` Search Resumes (round 1): scored all 100 resumes with hybrid RAG; 14 meet every hard requirement; kept the top 10: Sanjay Kulkarni (92), Hemant Joshi (90), Meera Krishnan (89), Kiran Rao (83), Harish Gupta (79), ...
- `rank_candidates` Rank Candidates (round 2): read 10 resumes in full, found 25 evidence lines, wrote strengths, gaps, and analyst notes (via LLM).
- `generate_report` Generate Report (round 3): 9 hire, 1 borderline, 0 no-hire; 0 ranking changes; saved reports/senior_python_backend_engineer_v1.md.

</details>

## Agent

**Senior Python Backend Engineer**: must-have Python, Django; nice-to-have Docker, query tuning; 5+ years.
Screened 100 resumes, kept the top 10, and deep-reviewed them: **9 hire, 1 borderline, 0 no-hire**.

| # | Candidate | Score | Years | Verdict | Main gap |
|---|---|---|---|---|---|
| 1 | Sanjay Kulkarni | 92 | 8 | HIRE | No evidence of nice-to-have: query tuning |
| 2 | Hemant Joshi | 90 | 7 | HIRE | No evidence of nice-to-have: query tuning |
| 3 | Meera Krishnan | 89 | 7 | HIRE | No evidence of nice-to-have: query tuning |
| 4 | Kiran Rao | 83 | 5 | HIRE | No evidence of nice-to-have: query tuning |
| 5 | Harish Gupta | 79 | 11 | HIRE | No evidence of nice-to-have: Docker, query tuning |
| 6 | Arjun Menon | 74 | 6 | HIRE | No evidence of nice-to-have: Docker, query tuning |
| 7 | Nagaraj | 73 | 4 | BORDERLINE | 4 years of experience, 1 short of the 5-year minimum |
| 8 | Arvind Swamy | 73 | 8 | HIRE | No evidence of nice-to-have: Docker, query tuning |
| 9 | Imran Sheikh | 71 | 9 | HIRE | No evidence of nice-to-have: Docker, query tuning |
| 10 | Anita Dsouza | 69 | 5 | HIRE | No evidence of nice-to-have: Docker, query tuning |

**Agent's take:** Interview Sanjay Kulkarni first because he has the highest score of 92 and strong containerization and database experience, making him the strongest fit among the top candidates. The most promising borderline candidate is Nagaraj, whose main gap is that he has only 4 years of experience, one year short of the 5‑year minimum.

Full report saved to `reports/senior_python_backend_engineer_v1.md`. Try: "Compare the top 3", "Why did Sanjay rank higher than Hemant?", "How could Nagaraj improve?", "Make <skill> a must-have", "done".

## You

done

<details><summary>Agent reasoning (1 steps)</summary>

- `human_feedback` Human Feedback: "done" -> intent done.

</details>

## Agent

Session finished. Start a new search any time.
