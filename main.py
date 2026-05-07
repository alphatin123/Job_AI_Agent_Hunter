#!/usr/bin/env python3
"""
CrewAI JobDB   Job Search Agent - Local Ollama Version
"""

import os
from datetime import datetime
from crewai import Agent, Task, Crew, Process
from crewai import LLM
from crewai_tools import SerperDevTool, ScrapeWebsiteTool

# ── Configuration ────────────────────────────────────────────────────────────

# Optional: Uncomment if you have Serper API key
# search_tool = SerperDevTool()
# scrape_tool = ScrapeWebsiteTool()

# ── Local LLM Setup (Optimized for 16GB RAM + 4GB VRAM) ─────────────────────
local_llm = LLM(
    model="ollama/qwen2.5:7b",          # Recommended (strong Chinese + English)
    # model="ollama/llama3.2:3b",       # Faster but lighter alternative
    base_url="http://localhost:11434",
    temperature=0.7,
    max_tokens=2048,
)

# ── Candidate Profile ───────────────────────────────────────────────────────
CANDIDATE_PROFILE = """
Your Profile 
"""

# ── Agents ───────────────────────────────────────────────────────────────────
job_researcher = Agent(
    role="JobDB Vacancy Researcher",
    goal="Search and collect the latest {Your Job Title}  and related {Your Job Title} job postings from JobDB Hong Kong.",
    backstory=(
        "You are an experienced Hong Kong IT recruitment analyst specializing in quickly finding "
        "relevant {Your Job Title} roles and extracting structured job information."#you can rewrite  your backstory 
    ),
    # tools=[search_tool, scrape_tool],   # Uncomment when using Serper
    llm=local_llm,
    verbose=True,
    max_iter=5,
)

cv_analyst = Agent(
    role="CV Matching Analyst",
    goal="Analyze the candidate's profile against each job posting and provide detailed matching scores, strengths, gaps, and recommendations.",
    backstory=(
        "You are a senior {Your Job Title} recruiter in Hong Kong with 10+ years of experience, "
        "specializing in assessing fresh graduates and entry-level candidates."
    ),
    llm=local_llm,
    verbose=True,
)

report_writer = Agent(
    role="Job Search Strategy Report Writer",
    goal="Generate a clear, professional, and actionable Traditional Chinese job search strategy report.",
    backstory=(
        "You are a professional career consultant who excels at turning complex data into "
        "easy-to-read, practical career advice."
    ),
    llm=local_llm,
    verbose=True,
)

# ── Tasks ────────────────────────────────────────────────────────────────────
task_search = Task(
    description=f"""
    Search for {Your Job Title} related positions in Hong Kong on JobDB.
    Focus on Junior and Entry-Level roles.
    
    Collect 6–8 recent job postings and output them in structured JSON format with the following fields:
    - job_title, company, salary_range, location, responsibilities, requirements, apply_url, posted_date
    """,
    expected_output="Structured JSON list containing multiple job postings",
    agent=job_researcher,
)

task_match = Task(
    description=f"""
    Using the candidate's profile below, perform a detailed matching analysis for each job:

    {CANDIDATE_PROFILE}

    For each job, provide:
    1. Matching Score (0–100)
    2. Strengths (2-3 points)
    3. Skill Gaps
    4. Application Recommendations
    5. Difficulty Level: Easy / Medium / Hard / Stretch

    #Pay special attention to positions open to fresh graduates (2026). if you are fresh graduates please delete #
    """,
    expected_output="Detailed matching analysis for each job in JSON format",
    agent=cv_analyst,
    context=[task_search],
)

task_report = Task(
    description="""
    Based on the previous tasks, generate a complete, professional Traditional Chinese job search strategy report.
    
    The report must include the following sections:
    ## 📊 Search Summary
    ## 🏆 Recommended Jobs (Match ≥60)
    ## 📋 Other Job References
    ## 🎯 Overall Job Search Strategy
    ## 📝 Action Plan
    """,
    expected_output="A well-formatted, professional Traditional Chinese Markdown report",
    agent=report_writer,
    context=[task_search, task_match],
    output_file="jobdb_report.md",
)

# ── Crew Assembly ───────────────────────────────────────────────────────────
crew = Crew(
    agents=[job_researcher, cv_analyst, report_writer],
    tasks=[task_search, task_match, task_report],
    process=Process.sequential,
    verbose=True,
)


def run():
    print("=" * 80)
    print("🔍 CrewAI JobDB  Job Search Agent (Local Ollama)")
    print(f" Started at : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f" Model       : {local_llm.model}")
    print("=" * 80)

    result = crew.kickoff()

    print("\n" + "=" * 80)
    print("✅ Mission Completed!")
    print("   Report saved as: jobdb_report.md")
    print("=" * 80)
    return result


if __name__ == "__main__":
    # Make sure Ollama is running before execution
    run()
