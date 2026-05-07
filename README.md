# 🔍 CrewAI JobDB Security Engineer 求職代理

專為 Tim Shing 設計的 AI 求職代理，自動搜尋 JobDB 香港的 Security Engineer 職缺，
並與你的 CV 進行匹配分析，輸出完整的求職策略報告。

---

## 架構說明

```
main.py
├── Agent 1: JobDB 職缺研究員    → 搜尋 & 抓取職缺資料
├── Agent 2: CV 匹配分析師       → 計算匹配分數 & 找出技能缺口
└── Agent 3: 求職策略報告師      → 生成完整 Markdown 報告
```

**流程（Sequential）：**
```
搜尋職缺 → 匹配分析 → 生成報告（jobdb_security_report.md）
```

---

## 快速開始

### 步驟 1：安裝環境

```bash
# 建議使用虛擬環境
python -m venv venv
source venv/bin/activate      # macOS / Linux
# venv\Scripts\activate       # Windows

pip install -r requirements.txt
```

### 步驟 2：設定 API Keys

```bash
cp .env.example .env
# 編輯 .env 填入你的 API Keys
```

取得 API Keys：
- **OpenAI**: https://platform.openai.com/api-keys（需付費，約 $0.01–0.05/次執行）
- **Serper**: https://serper.dev（免費，2,500 次/月）

### 步驟 3：執行代理

```bash
python main.py
```

執行時間約 **3–8 分鐘**，完成後自動生成 `jobdb_security_report.md`。

---

## 輸出範例

```markdown
## 🏆 推薦申請職缺

### 1. Junior Security Engineer — CyberTech HK Ltd
- 匹配分數: 82/100 ｜ 難度: Medium
- 薪資: HKD 18,000–22,000
- 優勢: Nessus/Nmap 經驗符合、Python 腳本能力、ISO 27001 知識
- 建議準備: 強調 CVE 研究項目、準備 penetration testing 案例
- 申請連結: https://www.jobdb.com/hk/job/...
```

---

## 費用估算

| 項目 | 費用 |
|------|------|
| OpenAI GPT-4o（每次執行） | 約 USD $0.05–0.15 |
| Serper Search（每次執行） | 約 5–10 次搜尋（免費額度內） |
| **每月執行 10 次** | 約 USD $1–2 |

---

## 進階設定

### 更換搜尋關鍵字

在 `main.py` 的 `task_search` 中修改搜尋詞：

```python
# 加入更多職位關鍵字
"Incident Response Analyst" Hong Kong
"Red Team" Hong Kong entry level
```

### 降低費用

```bash
# 在 .env 中改用較便宜的模型
OPENAI_MODEL_NAME=gpt-4o-mini
```

### 擴展到其他平台

可在 `task_search` 中加入：
- LinkedIn: `site:linkedin.com/jobs "security engineer" "hong kong"`
- Indeed HK: `site:hk.indeed.com "security engineer"`

---

## 注意事項

- 此代理**不會自動投遞申請**，JobDB 需要登入帳號才能申請
- 報告生成後，請手動前往各職缺連結進行申請
- 建議每週執行一次以獲取最新職缺
- 部分職缺連結可能因網頁抓取限制而不完整，需手動確認

---

## 檔案結構

```
jobdb_crew/
├── main.py                    # 主程式
├── requirements.txt           # 套件依賴
├── .env.example               # API Keys 範本
├── .env                       # 你的 API Keys（勿上傳 Git）
├── README.md                  # 本說明文件
└── jobdb_security_report.md  # 執行後自動生成的報告
```
