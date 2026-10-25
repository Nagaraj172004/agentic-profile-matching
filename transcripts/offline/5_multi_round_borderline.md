# 5_multi_round_borderline

## You

jobs/ml_engineer.txt

<details><summary>Agent reasoning (5 steps)</summary>

- `parse_jd` Parse JD: read job description from jobs/ml_engineer.txt (315 characters, structured header).
- `extract_requirements` Extract Requirements: must-have Python, PyTorch; nice-to-have Machine Learning, Deep Learning, NLP; minimum 3 years (via rules).
- `search_resumes` Search Resumes (round 1): scored all 100 resumes with hybrid RAG; 10 meet every hard requirement; kept the top 10: Aditi Rao (77), Vivek Nambiar (75), Karan Singh (72), Nikhil Verma (72), Tanvi Desai (71), ...
- `rank_candidates` Rank Candidates (round 2): read 10 resumes in full, found 32 evidence lines, wrote strengths, gaps, and analyst notes (via rules).
- `generate_report` Generate Report (round 3): 5 hire, 5 borderline, 0 no-hire; 0 ranking changes; saved reports/machine_learning_engineer_v1.md.

</details>

## Agent

**Machine Learning Engineer**: must-have Python, PyTorch; nice-to-have Machine Learning, Deep Learning, NLP; 3+ years.
Screened 100 resumes, kept the top 10, and deep-reviewed them: **5 hire, 5 borderline, 0 no-hire**.

| # | Candidate | Score | Years | Verdict | Main gap |
|---|---|---|---|---|---|
| 1 | Aditi Rao | 77 | 4 | HIRE | No evidence of nice-to-have: Deep Learning, NLP |
| 2 | Vivek Nambiar | 75 | 7 | HIRE | No evidence of nice-to-have: Deep Learning, NLP |
| 3 | Karan Singh | 72 | 5 | HIRE | No evidence of nice-to-have: Deep Learning, NLP |
| 4 | Nikhil Verma | 72 | 6 | HIRE | No evidence of nice-to-have: Machine Learning |
| 5 | Tanvi Desai | 71 | 8 | HIRE | No evidence of nice-to-have: Machine Learning |
| 6 | Radhika Menon | 63 | 2 | BORDERLINE | 2 years of experience, 1 short of the 3-year minimum |
| 7 | Shreya Bose | 60 | 3 | BORDERLINE | fit score below the hire bar of 65 |
| 8 | Ojas Patil | 54 | 4 | BORDERLINE | fit score below the hire bar of 65 |
| 9 | Qasim Ali | 53 | 6 | BORDERLINE | fit score below the hire bar of 65 |
| 10 | Uday Bhaskar | 46 | 5 | BORDERLINE | fit score below the hire bar of 65 |

Full report saved to `reports/machine_learning_engineer_v1.md`. Try: "Compare the top 3", "Why did Aditi rank higher than Vivek?", "How could Radhika Menon improve?", "Make <skill> a must-have", "done".

## You

Generate interview questions for Radhika Menon

<details><summary>Agent reasoning (2 steps)</summary>

- `human_feedback` Human Feedback: "Generate interview questions for Radhika Menon" -> intent questions.
- `agent` Agent: LLM unavailable, answered with rule-based tools.

</details>

## Agent

Screening questions for **Radhika Menon**:
1. Walk me through the most complex Python work you have shipped. What trade-offs did you make?
2. Walk me through the most complex PyTorch work you have shipped. What trade-offs did you make?
3. You have 2 years of experience and the role asks for 3. Which projects show senior-level ownership?
4. Have you worked with Deep Learning? If not, what have you used instead?
5. Describe how you would approach the first 90 days as a Machine Learning Engineer.
6. Tell me about a production incident you owned end to end. What did you change afterwards?

## You

How could Radhika Menon improve to become a hire?

<details><summary>Agent reasoning (2 steps)</summary>

- `human_feedback` Human Feedback: "How could Radhika Menon improve to become a hire?" -> intent candidate_detail.
- `agent` Agent: LLM unavailable, answered with rule-based tools.

</details>

## Agent

**Radhika Menon**: #6, score 63, verdict borderline. One gap (1 year more of experience needed); otherwise a relevant profile with a score of 63.
Strengths:
- Has every listed must-have: Python, PyTorch
- Brings nice-to-have skills: Machine Learning
- Resume wording closely matches the role (75% similarity)
Gaps:
- 2 years of experience, 1 short of the 3-year minimum
- No evidence of nice-to-have: Deep Learning, NLP
Improvement suggestions:
- Has 2 of 3 required years; consider for a mid-level opening, or revisit after 1 year more.
- Adding Deep Learning experience would strengthen the profile.
- Adding NLP experience would strengthen the profile.
