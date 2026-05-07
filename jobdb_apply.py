"""
JobDB 自動求職腳本（Playwright）
- 憑證在本機輸入，不傳送到任何外部服務
- 每次投遞前會顯示預覽，由你確認後才送出
- 需先執行 CrewAI 代理產生 jobdb_security_report.md
"""

import asyncio
import json
import re
import sys
from pathlib import Path
from getpass import getpass
from datetime import datetime
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout

# ── 設定區 ─────────────────────────────────────────────────────────────────
JOBDB_BASE      = "https://www.jobdb.com/hk"
JOBDB_LOGIN_URL = "https://www.jobdb.com/hk/en/jobseeker/login"
REPORT_FILE     = "jobdb_security_report.md"   # CrewAI 生成的報告
MAX_APPLY       = 10                            # 單次最多投遞數量上限
HEADLESS        = False                         # False = 顯示瀏覽器視窗（方便確認）

# 履歷路徑（若 JobDB 支援上傳履歷）
CV_FILE = Path("TimShing_offensive_security_CV.docx")

# 預設求職信模板（可依職缺自動填寫）
COVER_LETTER_TEMPLATE = """
Dear Hiring Manager,

I am writing to express my strong interest in the {job_title} position at {company}.

As a final-year Ethical Hacking and Cyber Security student (expected graduation June 2026),
I have hands-on experience in vulnerability assessment using Nessus and Nmap,
Python exploit scripting (including CVE-2024-49113 research), and
ISO 27001-aligned security control implementation.

During my internship at Top Level Corporation, I gained practical incident response
experience in a healthcare IT environment. My Final Year Project on automated
scanning and exploitation workflows directly aligns with the technical requirements
of this role.

I am eager to contribute to {company}'s security objectives and am available for
interview at your convenience.

Best regards,
Tim Shing
aae12518@gmail.com
""".strip()

# ── 從 Markdown 報告解析推薦職缺 ────────────────────────────────────────────
def parse_recommended_jobs(report_path: str) -> list[dict]:
    """
    解析 CrewAI 生成的 Markdown 報告，提取推薦職缺列表。
    若報告不存在，回傳空列表（腳本仍可搜尋新職缺）。
    """
    path = Path(report_path)
    if not path.exists():
        print(f"⚠️  找不到報告 {report_path}，將使用直接搜尋模式")
        return []

    jobs = []
    content = path.read_text(encoding="utf-8")

    # 解析格式: ### N. 職位名稱 — 公司名稱
    pattern = re.compile(
        r"###\s+\d+\.\s+(.+?)\s+—\s+(.+?)\n"   # title, company
        r".*?申請連結[:：]\s*(https?://\S+)",     # apply_url
        re.DOTALL,
    )
    for m in pattern.finditer(content):
        jobs.append({
            "title":     m.group(1).strip(),
            "company":   m.group(2).strip(),
            "apply_url": m.group(3).strip(),
        })

    return jobs


# ── 確認投遞（互動式） ────────────────────────────────────────────────────
def confirm_apply(job: dict, index: int, total: int) -> bool:
    print(f"\n{'─'*55}")
    print(f"  [{index}/{total}] 即將投遞")
    print(f"  職位: {job['title']}")
    print(f"  公司: {job['company']}")
    print(f"  連結: {job.get('apply_url', '（搜尋結果）')}")
    print(f"{'─'*55}")
    ans = input("  確認投遞？[y/N/q=全部停止] > ").strip().lower()
    if ans == "q":
        print("已停止所有投遞。")
        sys.exit(0)
    return ans == "y"


# ── 主流程 ───────────────────────────────────────────────────────────────────
async def main():
    print("=" * 55)
    print("  JobDB 自動求職腳本")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 55)

    # 本機輸入憑證（不傳送到任何外部服務）
    print("\n請輸入你的 JobDB 帳號（憑證只在本機使用）")
    email    = input("  Email: ").strip()
    password = getpass("  密碼: ")

    # 載入推薦職缺
    jobs = parse_recommended_jobs(REPORT_FILE)
    if jobs:
        print(f"\n✅ 從報告載入 {len(jobs)} 個推薦職缺")
    else:
        print("\n⚠️  將搜尋 JobDB 上的 Security Engineer 職缺")

    applied     = []
    skipped     = []
    failed      = []
    apply_count = 0

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=HEADLESS, slow_mo=800)
        ctx     = await browser.new_context(
            viewport={"width": 1280, "height": 900},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/135.0.0.0 Safari/537.36"
            ),
        )
        page = await ctx.new_page()

        # ── 登入 ──────────────────────────────────────────────────────
        print(f"\n🔐 登入 JobDB...")
        await page.goto(JOBDB_LOGIN_URL, wait_until="domcontentloaded")
        await page.wait_for_timeout(1500)

        try:
            await page.fill('input[type="email"], input[name="email"]', email)
            await page.fill('input[type="password"], input[name="password"]', password)
            await page.click('button[type="submit"], input[type="submit"]')
            await page.wait_for_url(re.compile(r"/dashboard|/jobseeker|/home"), timeout=12000)
            print("✅ 登入成功")
        except PlaywrightTimeout:
            print("❌ 登入失敗或跳驗證，請手動在瀏覽器視窗完成登入")
            print("   完成後按 Enter 繼續...")
            input()

        # ── 若無推薦職缺，搜尋 JobDB ──────────────────────────────────
        if not jobs:
            print("\n🔍 搜尋 Security Engineer 職缺...")
            search_url = (
                f"{JOBDB_BASE}/en/job-search"
                f"?q=security+engineer&l=Hong+Kong&industry=IT"
            )
            await page.goto(search_url, wait_until="domcontentloaded")
            await page.wait_for_timeout(2000)

            # 抓取搜尋結果中的職缺連結
            job_cards = await page.query_selector_all(
                'a[href*="/job/"], a[href*="/en/job/"]'
            )
            for card in job_cards[:MAX_APPLY]:
                href  = await card.get_attribute("href")
                title = (await card.inner_text()).strip()[:60]
                if href and "/job/" in href:
                    jobs.append({
                        "title":     title or "Security Engineer",
                        "company":   "（待確認）",
                        "apply_url": href if href.startswith("http") else JOBDB_BASE + href,
                    })
            print(f"   找到 {len(jobs)} 個職缺")

        # ── 逐一投遞 ──────────────────────────────────────────────────
        total = min(len(jobs), MAX_APPLY)
        print(f"\n📋 準備投遞 {total} 個職缺（每次都會請你確認）\n")

        for i, job in enumerate(jobs[:total], 1):
            if apply_count >= MAX_APPLY:
                print(f"\n已達單次上限 {MAX_APPLY} 個，停止投遞。")
                break

            if not confirm_apply(job, i, total):
                skipped.append(job["title"])
                continue

            try:
                await page.goto(job["apply_url"], wait_until="domcontentloaded")
                await page.wait_for_timeout(2000)

                # 點擊 Apply Now 按鈕
                apply_btn = await page.query_selector(
                    'a:has-text("Apply Now"), button:has-text("Apply"), '
                    'a:has-text("Easy Apply"), button:has-text("Quick Apply")'
                )
                if not apply_btn:
                    print(f"   ⚠️  找不到申請按鈕，請手動操作")
                    failed.append(job["title"])
                    continue

                await apply_btn.click()
                await page.wait_for_timeout(2000)

                # 填寫求職信（若有欄位）
                cover_letter_area = await page.query_selector(
                    'textarea[name*="cover"], textarea[placeholder*="cover"], '
                    'textarea[name*="letter"], textarea[id*="cover"]'
                )
                if cover_letter_area:
                    cl_text = COVER_LETTER_TEMPLATE.format(
                        job_title=job["title"],
                        company=job["company"],
                    )
                    await cover_letter_area.fill(cl_text)
                    print("   ✍️  已填寫求職信")

                # 上傳 CV（若有上傳欄位且檔案存在）
                if CV_FILE.exists():
                    upload_input = await page.query_selector('input[type="file"]')
                    if upload_input:
                        await upload_input.set_input_files(str(CV_FILE))
                        print("   📎 已上傳 CV")

                # 最後確認送出
                print("   ⏳ 請在瀏覽器確認資料無誤後，腳本將自動點擊送出...")
                await page.wait_for_timeout(3000)

                submit_btn = await page.query_selector(
                    'button[type="submit"]:has-text("Submit"), '
                    'button:has-text("Send Application"), '
                    'input[type="submit"]'
                )
                if submit_btn:
                    await submit_btn.click()
                    await page.wait_for_timeout(2000)
                    print(f"   ✅ 已投遞：{job['title']} @ {job['company']}")
                    applied.append(job["title"])
                    apply_count += 1
                else:
                    print("   ⚠️  找不到送出按鈕，請手動完成送出")
                    input("   （完成後按 Enter 繼續下一個）")
                    applied.append(job["title"] + "（手動）")
                    apply_count += 1

                await page.wait_for_timeout(1500)

            except Exception as e:
                print(f"   ❌ 投遞失敗: {e}")
                failed.append(job["title"])

        await browser.close()

    # ── 結果摘要 ─────────────────────────────────────────────────────
    print(f"\n{'='*55}")
    print(f"  投遞完成摘要")
    print(f"{'='*55}")
    print(f"  ✅ 成功投遞: {len(applied)} 個")
    for t in applied:
        print(f"     • {t}")
    if skipped:
        print(f"  ⏭️  跳過: {len(skipped)} 個")
    if failed:
        print(f"  ❌ 失敗:  {len(failed)} 個")
        for t in failed:
            print(f"     • {t}")

    # 輸出投遞記錄
    log = {
        "date": datetime.now().isoformat(),
        "applied": applied,
        "skipped": skipped,
        "failed": failed,
    }
    Path("apply_log.json").write_text(json.dumps(log, ensure_ascii=False, indent=2))
    print(f"\n  📄 投遞記錄已儲存至 apply_log.json")


if __name__ == "__main__":
    asyncio.run(main())
