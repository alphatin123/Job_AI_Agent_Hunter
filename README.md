# 🔍 CrewAI JobDB Job Search Agent  


---

## Architecture Overview

```
main.py
├── Agent 1: JobDB Vacancy Researcher → Searches & extracts job postings
├── Agent 2: CV Matching Analyst → Calculates matching scores & identifies skill gaps
└── Agent 3: Job Search Strategy Reporter → Generates complete Markdown report
```

**Workflow (Sequential):：**
```
Job Search → CV Matching Analysis → Report Generation (`jobdb_security_report.md`)
```

---

## Quick Start

### Install Environment

```bash
# 建議使用虛擬環境
python -m venv venv
source venv/bin/activate      # macOS / Linux
# venv\Scripts\activate       # Windows

pip install -r requirements.txt
```

### Configure API Keys or you can use ollma if no API key

```bash
cp .env.example .env
# Edit the .env file and add your API keys
```

Obtain API Keys:
OpenAI: https://platform.openai.com/api-keys (Paid, approx. $0.01–$0.05 per run)
Serper: https://serper.dev (Free tier: 2,500 searches/month)

Step 3: Run the Agent

```bash
python main.py
```
Execution time: Approximately 3–8 minutes.
Upon completion, the report jobdb_security_report.md will be automatically generated.

---

## Output Example

```markdown
## 🏆 Recommended Job Applications

- **Matching Score**: 82/100 | Difficulty: Medium
- **Salary**: HKD 18,000–22,000
- **Strengths**: Nessus/Nmap experience matches, Python scripting skills, ISO 27001 knowledge
- **Recommendations**: Highlight CVE research projects, prepare penetration testing case studies
- **Apply Here**: https://www.jobdb.com/hk/job/...
```

---

## Cost Estimation

Item,Cost
OpenAI GPT-4o (per run),Approx. USD $0.05 – $0.15
Serper Search (per run),5–10 searches (within free quota)
10 runs per month,Approx. USD $1 – $2

---

## Advanced Configuration

### Change Search Keywords

Edit the search terms in main.py under task_search:

```python
# Add more job title keywords
"Job Title" Hong Kong
"Job Title" Hong Kong entry level
```

### Reduce Costs

```bash
# Use a cheaper model in .env
OPENAI_MODEL_NAME=gpt-4o-mini
```

### Expand to Other Platforms

You can add the following in task_search:
-LinkedIn: site:linkedin.com/jobs "security engineer" "hong kong"
-Indeed HK: site:hk.indeed.com "your job title"

---

## Important Notes

-This agent does not submit applications automatically. JobDB requires you to log in to apply.
-After the report is generated, please manually visit each job link to submit your application.
-It is recommended to run the agent once per week to get the latest job openings.
-Some job links may be incomplete due to web scraping limitations — please verify manually.

---

## Project Structure

```
jobdb_crew/
├── main.py                    # Run with: python3 main.py
├── requirements.txt           # Installation requirements
├── .env.example               # API Keys template
├── .env                       # API Keys (do not upload to Git)
├── README.md                  # Project description
└── jobdb_security_report.md   # Generated automation report
```
