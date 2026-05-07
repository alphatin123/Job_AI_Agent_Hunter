#!/usr/bin/env python3
"""
CrewAI JobDB Security Engineer 求職代理 - 本地 Ollama 版本
"""

import os
from datetime import datetime
from crewai import Agent, Task, Crew, Process
from crewai import LLM
from crewai_tools import SerperDevTool, ScrapeWebsiteTool

# ── 環境設定 ────────────────────────────────────────────────────────────────
# 如果你還有 Serper API Key，可以繼續用；沒有也可以先註解掉 search_tool
#search_tool = SerperDevTool()      # 需要 SERPER_API_KEY 在 .env
#scrape_tool = ScrapeWebsiteTool()

# ── 本地 LLM 設定（適合你的 16GB RAM + 4GB VRAM） ─────────────────────────────
local_llm = LLM(
    #model="ollama/llama3.2:3b",      # 先用這個測試，速度最快
    model="ollama/qwen2.5:7b",     # 之後可換這個（中文較強）
    base_url="http://localhost:11434",
    temperature=0.7,
    max_tokens=2048,
)

# ── 求職者 CV 摘要 ─────────────────────────────────────────────────────────
CANDIDATE_PROFILE = """
姓名: Tim Shing
學歷: Bachelor's Degree in Ethical Hacking and Cyber Security (預計 2026 年 6 月畢業)
語言: 廣東話（母語）、英語（中級）、普通話（母語）
工作經驗:
  - Top Level Corporation Limited (IT Service Provider) 實習生 2023/09–2023/11
    • 協助醫院電子郵件升級談判
    • 管理 email archive server 備份與同步

技術專長:
  - 弱點掃描: Nessus, Nmap
  - 滲透測試: Python exploit POC開發
  - CVE 研究: CVE-2024-49113 (LDAP DoS, Windows 未加密 port 389)
  - Windows 安全: Defender bypass, 不安全反序列化漏洞分析
  - 框架: ISO 27001 安全控制實施
  - 風險評估 & 滲透測試報告撰寫

證照/競賽: CTF 競賽 2024 (HKIRCL)

求職目標: Security Engineer (Hong Kong, 可接受 Entry-Level / Junior)
"""

# ── Agents 定義 ──────────────────────────────────────────────────────────────
job_researcher = Agent(
    role="JobDB 職缺研究員",
    goal="在 JobDB 香港平台上搜尋 Security Engineer、Cybersecurity Analyst、Penetration Tester、SOC Analyst 等相關職缺，收集詳細職缺資訊。",
    backstory="你是一位專業的香港 IT 就業市場分析師，擅長從 JobDB 快速找到最新且符合條件的資安職缺，並提取結構化資訊。",
    #tools=[search_tool, scrape_tool],
    llm=local_llm,
    verbose=True,
    max_iter=4,           # 降低避免無限循環
)

cv_analyst = Agent(
    role="CV 與職缺匹配分析師",
    goal="根據求職者 CV 與每個職缺進行詳細匹配分析，給出匹配分數、優勢、缺口與申請建議。",
    backstory="你是一位擁有10年經驗的香港資安領域獵頭，擅長精準評估應屆畢業生與 Entry-Level 職位的匹配度。",
    llm=local_llm,
    verbose=True,
)

report_writer = Agent(
    role="求職策略報告撰寫師",
    goal="將職缺搜尋與匹配分析結果整理成清晰、實用的繁體中文求職策略報告。",
    backstory="你是一位專業職涯顧問，擅長把複雜資訊整理成易讀的行動計劃。",
    llm=local_llm,
    verbose=True,
)

# ── Tasks 定義 ───────────────────────────────────────────────────────────────
task_search = Task(
    description=f"""
    在 JobDB 香港搜尋 Security Engineer 相關職缺（包含 Junior、Entry Level）。
    重點關鍵字：Security Engineer, Cybersecurity Analyst, Penetration Tester, SOC Analyst, Information Security。
    請盡量收集 6–8 個最新職缺，並以結構化 JSON 格式輸出每個職缺的以下資訊：
    - job_title, company, salary_range, location, responsibilities, requirements, apply_url, posted_date
    """,
    expected_output="一份包含多個職缺的結構化 JSON 列表",
    agent=job_researcher,
)

task_match = Task(
    description=f"""
    使用以下求職者資料，對找到的每個職缺進行匹配分析：

    {CANDIDATE_PROFILE}

    對每個職缺請輸出：
    1. 匹配分數（0–100）
    2. 優勢（2-3點）
    3. 技能缺口
    4. 申請建議
    5. 難度評級：Easy / Medium / Hard / Stretch

    特別優先考慮接受應屆畢業生（2026年畢業）的 Entry-Level 職位。
    """,
    expected_output="每個職缺的詳細匹配分析（JSON 格式）",
    agent=cv_analyst,
    context=[task_search],
)

task_report = Task(
    description="""
    根據前面兩個任務的結果，生成一份完整的繁體中文求職策略報告。
    報告需包含以下章節：
    ## 📊 搜尋結果摘要
    ## 🏆 推薦申請職缺（匹配 ≥60 分）
    ## 📋 其他職缺參考
    ## 🎯 整體求職策略建議
    ## 📝 下一步行動清單
    """,
    expected_output="一份格式完整、美觀的繁體中文 Markdown 求職報告",
    agent=report_writer,
    context=[task_search, task_match],
    output_file="jobdb_security_report.md",
)

# ── Crew 組建 ───────────────────────────────────────────────────────────────
crew = Crew(
    agents=[job_researcher, cv_analyst, report_writer],
    tasks=[task_search, task_match, task_report],
    process=Process.sequential,
    verbose=True,
)

def run():
    print("=" * 70)
    print("🔍 CrewAI JobDB Security Engineer 求職代理（本地 Ollama 版本）")
    print(f"   執行時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   使用模型: {local_llm.model}")
    print("=" * 70)

    result = crew.kickoff()

    print("\n" + "=" * 70)
    print("✅ 任務完成！報告已儲存至：jobdb_security_report.md")
    print("=" * 70)
    return result


if __name__ == "__main__":
    # 建議先確保 Ollama 正在運行
    run()
