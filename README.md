# NewsLens｜AI 新聞摘要系統

使用 **Python + uv + Gemini API** 將新聞原文整理成 **繁體中文摘要、三大重點、關鍵字、分類**，透過 **GitHub Actions** 自動測試及部署 **GitHub Pages**。課堂作業對應能力：**JSON 結構化輸出**。

> ⚠️ 此專案隨附的校園文章是自創虛構的測試文本，不是實際新聞。沒有 API Key 時可用示範模式檢查排版；示範結果不是 AI 生成。

## 功能

1. 讀取 `data/news.txt` 中的新聞文字。
2. `src/main.py` 透過 Gemini REST `generateContent` 呼叫 LLM。
3. 使用 `responseMimeType: application/json` 和 `responseSchema` 約束模型的輸出結構。
4. Python 驗證標題、摘要、三項重點、關鍵字、分類並產生 `docs/result.json`。
5. 靜態 `docs/index.html` 載入 JSON 呈現成果。
6. GitHub Actions 自動測試、執行摘要程式、部署 Pages。

## 專案結構

```text
ai-news-summarizer/
├── .github/workflows/deploy.yml  # Actions 自動部署
├── data/news.txt                 # 新聞文字輸入（虛構範例）
├── src/main.py                  # LLM 呼叫及 JSON 驗證
├── tests/test_main.py           # 單元測試
├── docs/index.html              # 作品網站四項內容
├── docs/result.json             # 程式產生結果
├── .env.example                 # 金鑰格式範例
├── .gitignore                   # 忽略機密資訊
├── pyproject.toml               # uv 專案
├── uv.lock                      # 鎖定檔
└── README.md
```

## 本機執行（Windows 11 / PowerShell）

### 1. 安裝 uv

官方指令（https://docs.astral.sh/uv/getting-started/installation/）：

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
uv --version
```

或使用 `winget install --id=astral-sh.uv -e`。

### 2. 安裝 Python 與依賴

```powershell
uv python install 3.12
uv sync --locked
```

本專案使用 Python 標準函式庫，無額外 pip 套件。

### 3. 取得 API Key 並安全設定

到 https://aistudio.google.com/apikey 建立 API Key。在專案根目錄執行：

```powershell
Copy-Item .env.example .env
notepad .env
```

將 `GEMINI_API_KEY=your_key_here` 改為自己的金鑰。**不要上傳 `.env`、不要將金鑰寫在網站 JavaScript，也不要將它複製到 README。**

### 4. 執行真實 AI 摘要

```powershell
uv run python src/main.py --mode ai
```

執行成功時，終端機會印出 JSON，`docs/result.json` 會被更新。你也可以用另一篇新聞內容替換 `data/news.txt` 後重跑（應有合法使用權限，並注意內容中的個資）。

沒有金鑰時只想看網站，可執行**非 AI**示範：

```powershell
uv run python src/main.py --mode demo
```

### 5. 執行測試與預覽網頁

```powershell
uv run python -m unittest discover -s tests -v
uv run python -m http.server 8000 --directory docs
```

開啟 http://localhost:8000 。切勿直接用 `file://` 開啟，否則瀏覽器可能阻擋讀取 JSON。

## GitHub 儲存庫與 Actions 自動部署

1. 在 GitHub 建立新的 **Public** repository，名稱建議 `ai-news-summarizer`。**不要勾選新增 README**（本專案已有）。
2. 在本機此資料夾執行 `git init`、`git branch -M main`、將檔案分批 `git add` 及 `git commit`，至少 5 個 commit（見下段）。
3. 前往 repo 的 **Settings → Secrets and variables → Actions → New repository secret**，名稱 `GEMINI_API_KEY`，值為你的 API Key。
4. **Settings → Pages → Build and deployment → Source：GitHub Actions**。
5. 在本機連接 repo：

```powershell
git remote add origin https://github.com/YOUR_USERNAME/ai-news-summarizer.git
git push -u origin main
```

6. 查看 **Actions**，確認 `Build AI News and Deploy Pages` workflow 有綠色勾勾。
7. 前往 **Settings → Pages** 找到公開作品頁網址，通常是 `https://YOUR_USERNAME.github.io/ai-news-summarizer/`。

> **注意：** 若 Secret 缺失，Actions 仍會部署「人工示範」頁面並明確標示；要證明 AI 功能須設定真實金鑰，重新執行 Actions（Re-run 或 workflow_dispatch），確認頁面標示「AI 真實生成」。若 AI 呼叫失敗會讓 Actions 失敗，請先檢查金鑰、模型權限及額度。使用 API 可能產生費用。

## 五次以上 commit 建議

請**真的依不同階段分批提交**，不可僅在 README 宣稱做過：

1. `chore: initialize uv project and ignore secrets`
2. `feat: add article input and Gemini summarizer`
3. `test: add JSON validation tests`
4. `feat: design GitHub Pages showcase`
5. `ci: add GitHub Actions deployment`
6. `docs: document execution and AI usage`

建議使用 `git log --oneline` 截圖，讓老師能確認完整歷程。

## AI 使用說明（請如實填寫）

- **工具：** Gemini API 用於執行階段的新聞摘要；ChatGPT 協助產生專案初稿（Python、網頁、README、測試、Actions）。
- **使用方式：** 以提示詞要求模型使用繁體中文，輸出 `headline`、`summary`、`key_points`、`keywords`、`category` JSON，程式再驗證欄位格式。
- **個人驗證紀錄（交作業前由本人更新）：**
  - [ ] 我已在本機執行 `uv sync --locked`。
  - [ ] 我已在本機執行 `uv run python src/main.py --mode ai`，確認真正呼叫 AI。
  - [ ] 我已執行單元測試並記錄測試結果。
  - [ ] 我已確認 Actions 執行成功，Pages 顯示「AI 真實生成」。
  - [ ] 我已自己檢查摘要有無超出原文或捏造資訊。
  - [ ] 我實際修改的檔案／原因：**（請本人填寫，不可虛構）**。

## 作品頁對應老師要求

| 老師要求 | 作品頁位置 |
|---|---|
| 做了什麼 | 01 About this project |
| 怎麼執行 | 03 How to run |
| 執行結果 | 02 Output showcase |
| AI 使用說明 | 04 AI disclosure |

## 限制與安全

- GitHub Pages 是**靜態網頁**，不會直接在瀏覽器使用你的 Secret。網站顯示 Actions 最近一次生成的結果，不是讓訪客輸入文字即時呼叫 AI。
- 如果摘要來源敏感，不應放進公開 `result.json` 或 Actions Logs。
- Gemini 可能產生錯誤，人工應對照原文驗證。
- `.env` 已列入 `.gitignore`；真正 Key 只放在本機或 GitHub Secrets。
