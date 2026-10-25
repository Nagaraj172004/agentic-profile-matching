# 6_edge_cases

## You

Find me candidates with Rust and Haskell and 10+ years experience

<details><summary>Agent reasoning (5 steps)</summary>

- `parse_jd` Parse JD: read job description from the message (65 characters, free text).
- `extract_requirements` Extract Requirements: must-have Rust, Haskell; nice-to-have none; minimum 10 years (via llm).
- `search_resumes` Search Resumes (round 1): scored all 100 resumes with hybrid RAG; 0 meet every hard requirement; kept the top 10: Chetan Bhat (0), Gopal Krishnan (0), Irfan Pathan (0), Zubin Mistry (0), Neelam Choudhary (0), ...
- `rank_candidates` Rank Candidates (round 2): read 10 resumes in full, found 0 evidence lines, wrote strengths, gaps, and analyst notes (via LLM).
- `generate_report` Generate Report (round 3): 0 hire, 0 borderline, 10 no-hire; 0 ranking changes; saved reports/senior_rust_haskell_engineer_v1.md.

</details>

## Agent

**Senior Rust/Haskell Engineer**: must-have Rust, Haskell; nice-to-have none; 10+ years.
Screened 100 resumes, kept the top 10, and deep-reviewed them: **0 hire, 0 borderline, 10 no-hire**.

| # | Candidate | Score | Years | Verdict | Main gap |
|---|---|---|---|---|---|
| 1 | Chetan Bhat | 0 | 6 | NO-HIRE | Missing must-have skill: Rust |
| 2 | Gopal Krishnan | 0 | 1 | NO-HIRE | Missing must-have skill: Rust |
| 3 | Irfan Pathan | 0 | 5 | NO-HIRE | Missing must-have skill: Rust |
| 4 | Zubin Mistry | 0 | 9 | NO-HIRE | Missing must-have skill: Rust |
| 5 | Neelam Choudhary | 0 | 5 | NO-HIRE | Missing must-have skill: Rust |
| 6 | Abhishek Tiwari | 0 | 4 | NO-HIRE | Missing must-have skill: Rust |
| 7 | Girish Nair | 0 | 6 | NO-HIRE | Missing must-have skill: Rust |
| 8 | Devendra Singh | 0 | 7 | NO-HIRE | Missing must-have skill: Rust |
| 9 | Siddharth Jain | 0 | 5 | NO-HIRE | Missing must-have skill: Rust |
| 10 | Karan Singh | 0 | 5 | NO-HIRE | Missing must-have skill: Rust |

**Agent's take:** None of the top candidates qualify for an interview because all lack the required Rust/Haskell skills and seniority. Therefore, we cannot interview anyone at this time. There are no borderline cases.

Full report saved to `reports/senior_rust_haskell_engineer_v1.md`. Try: "Compare the top 3", "Why did Chetan rank higher than Gopal?", "Make <skill> a must-have", "done".

## You

Compare John Doe and Jane Smith

<details><summary>Agent reasoning (3 steps)</summary>

- `human_feedback` Human Feedback: "Compare John Doe and Jane Smith" -> intent compare.
- `agent` Agent: forced compare_candidates failed (Error code: 429 - {'error': {'message': 'Rate limit reached for model `openai/gpt-oss-20b` in organization `org_01m40kmq); retrying.
- `agent` Agent: answered after 0 tool round(s).

</details>

## Agent

I don’t have any records for “John Doe” or “Jane Smith” in the current shortlist.  
If you’d like to compare other candidates that are in the list, let me know their IDs or ranks (e.g., “#1” or “chetan_bhat”).

## You

Drop Rust and Haskell, require Golang with 4+ years instead

<details><summary>Agent reasoning (5 steps)</summary>

- `human_feedback` Human Feedback: "Drop Rust and Haskell, require Golang with 4+ years instead" -> intent refine.
- `extract_requirements` Extract Requirements: applied "Drop Rust and Haskell, require Golang with 4+ years instead" -> Golang is now a must-have; Rust is no longer a must-have; Haskell is no longer a must-have; minimum years changed from 10 to 4 (via rules).
- `search_resumes` Search Resumes (round 1): scored all 100 resumes with hybrid RAG; 2 meet every hard requirement; kept the top 10: Pranav Hegde (57), Jaya Prakash (57), Gopal Krishnan (0), Farhan Qureshi (0), Charu Goel (0), ...
- `rank_candidates` Rank Candidates (round 2): read 10 resumes in full, found 2 evidence lines, wrote strengths, gaps, and analyst notes (via rules).
- `generate_report` Generate Report (round 3): 0 hire, 2 borderline, 8 no-hire; 17 ranking changes; saved reports/candidates_with_golang_v2.md.

</details>

## Agent

**Candidates with Golang**: must-have Golang; nice-to-have none; 4+ years.
Screened 100 resumes, kept the top 10, and deep-reviewed them: **0 hire, 2 borderline, 8 no-hire**.

**Requirement change:** Golang is now a must-have; Rust is no longer a must-have; Haskell is no longer a must-have; minimum years changed from 10 to 4.

**How the ranking moved:**
- Pranav Hegde entered the top 10 at #1 (score 0 -> 57): Rust is no longer required; Haskell is no longer required; has newly listed skill Golang; now meets the 4-year minimum
- Jaya Prakash entered the top 10 at #2 (score 0 -> 57): Rust is no longer required; Haskell is no longer required; has newly listed skill Golang; now meets the 4-year minimum
- Gopal Krishnan moved down from #2 to #3 (score 0 -> 0): does not have new must-have Golang; Rust is no longer required; Haskell is no longer required
- Farhan Qureshi entered the top 10 at #4 (score 0 -> 0): does not have new must-have Golang; Rust is no longer required; Haskell is no longer required; now meets the 4-year minimum
- Charu Goel entered the top 10 at #5 (score 0 -> 0): does not have new must-have Golang; Rust is no longer required; Haskell is no longer required; now meets the 4-year minimum
- Vikram Patel entered the top 10 at #6 (score 0 -> 0): does not have new must-have Golang; Rust is no longer required; Haskell is no longer required; now meets the 4-year minimum
- Suresh Babu entered the top 10 at #8 (score 0 -> 0): does not have new must-have Golang; Rust is no longer required; Haskell is no longer required; now meets the 4-year minimum
- Omar Farooq entered the top 10 at #9 (score 0 -> 0): does not have new must-have Golang; Rust is no longer required; Haskell is no longer required; now meets the 4-year minimum

| # | Candidate | Score | Years | Verdict | Main gap |
|---|---|---|---|---|---|
| 1 | Pranav Hegde | 57 | 9 | BORDERLINE | fit score below the hire bar of 65 |
| 2 | Jaya Prakash | 57 | 5 | BORDERLINE | fit score below the hire bar of 65 |
| 3 | Gopal Krishnan | 0 | 1 | NO-HIRE | Missing must-have skill: Golang |
| 4 | Farhan Qureshi | 0 | 8 | NO-HIRE | Missing must-have skill: Golang |
| 5 | Charu Goel | 0 | 5 | NO-HIRE | Missing must-have skill: Golang |
| 6 | Vikram Patel | 0 | 8 | NO-HIRE | Missing must-have skill: Golang |
| 7 | Girish Nair | 0 | 6 | NO-HIRE | Missing must-have skill: Golang |
| 8 | Suresh Babu | 0 | 9 | NO-HIRE | Missing must-have skill: Golang |
| 9 | Omar Farooq | 0 | 6 | NO-HIRE | Missing must-have skill: Golang |
| 10 | Bharat Varma | 0 | 4 | NO-HIRE | Missing must-have skill: Golang |

Full report saved to `reports/candidates_with_golang_v2.md`. Try: "Compare the top 3", "Why did Pranav rank higher than Jaya?", "How could Pranav Hegde improve?", "Make <skill> a must-have", "done".
