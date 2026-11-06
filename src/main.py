"""AI 新聞摘要：讀取本地文字 → Gemini REST API → 驗證 JSON → 產生靜態網頁資料。"""
from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "data" / "news.txt"
OUTPUT = ROOT / "docs" / "result.json"
MODEL_DEFAULT = "gemini-2.5-flash"

SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "headline": {"type": "STRING"},
        "summary": {"type": "STRING"},
        "key_points": {"type": "ARRAY", "items": {"type": "STRING"}},
        "keywords": {"type": "ARRAY", "items": {"type": "STRING"}},
        "category": {"type": "STRING"},
    },
    "required": ["headline", "summary", "key_points", "keywords", "category"],
}


def load_local_env() -> None:
    """支援簡單 .env（無需第三方套件）；不覆蓋已有環境變數。"""
    env_path = ROOT / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8-sig").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


def validate_result(obj: object) -> dict:
    if not isinstance(obj, dict):
        raise ValueError("LLM 結果不是 JSON 物件")
    for field in ("headline", "summary", "category"):
        if not isinstance(obj.get(field), str) or not obj[field].strip():
            raise ValueError(f"缺少非空文字欄位：{field}")
    for field in ("key_points", "keywords"):
        items = obj.get(field)
        if not isinstance(items, list) or not items or not all(
            isinstance(item, str) and item.strip() for item in items
        ):
            raise ValueError(f"欄位 {field} 必須是非空文字陣列")
    if len(obj["key_points"]) != 3:
        raise ValueError("key_points 必須剛好有三項")
    return {field: obj[field] for field in ("headline", "summary", "key_points", "keywords", "category")}


def summarize_with_gemini(article: str, api_key: str, model: str) -> dict:
    if not api_key or api_key == "your_key_here":
        raise ValueError("GEMINI_API_KEY 未設定")
    # 模型名稱只接受預期字元，避免網址路徑注入。
    if not model or not all(c.isalnum() or c in "-_." for c in model):
        raise ValueError("GEMINI_MODEL 名稱格式不正確")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    prompt = (
        "你是謹慎的繁體中文新聞編輯。根據以下提供的文章內容摘要，不要補充原文未提及的事實。"
        "回傳 JSON：headline 精簡標題、summary 80-130 字摘要、key_points 剛好三項重點、"
        "keywords 3-5 個關鍵字、category 一個主題類別。"
        "保留不確定性，尤其不可把試辦計畫說成已完成。文章若標示虛構，仍照內容摘要。\n\n"
        + article[:14000]
    )
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseMimeType": "application/json",
            "responseSchema": SCHEMA,
            "temperature": 0.2,
        },
    }
    request = Request(
        url,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json", "x-goog-api-key": api_key},
        method="POST",
    )
    try:
        with urlopen(request, timeout=60) as response:
            raw = json.load(response)
    except HTTPError as exc:
        # 不記錄 API Key 或完整敏感 request。
        detail = exc.read(700).decode("utf-8", errors="replace")
        raise RuntimeError(f"Gemini API HTTP {exc.code}：{detail}") from exc
    except URLError as exc:
        raise RuntimeError(f"無法連接 Gemini API：{exc.reason}") from exc
    try:
        generated = raw["candidates"][0]["content"]["parts"][0]["text"]
        return validate_result(json.loads(generated))
    except (KeyError, IndexError, TypeError, json.JSONDecodeError, ValueError) as exc:
        raise RuntimeError("AI 回傳資料格式不正確或內容遭阻擋") from exc


def demo_result() -> dict:
    # 這是人工編寫的示範資料，絕不宣稱由 AI 產生。
    return {
        "headline": "校園試辦智慧回收站，八週後評估成效",
        "summary": "某大學在圖書館與學生餐廳附近試辦兩座智慧回收站，透過螢幕提示垃圾分類規則，並彙整每日回收量。試辦預計持續八週，校方將蒐集數據及學生意見，再決定是否擴大設置；目前尚未公布實際減碳成效。",
        "key_points": [
            "在兩處校園空間試辦智慧回收站，提供分類提醒。",
            "計畫持續八週，期間會彙整回收量與使用意見。",
            "目前無減碳成效數據，是否擴大設置仍待評估。",
        ],
        "keywords": ["智慧回收站", "垃圾分類", "校園永續", "試辦計畫"],
        "category": "校園／環境",
    }


def build(mode: str, input_path: Path, output_path: Path) -> dict:
    article = input_path.read_text(encoding="utf-8-sig").strip()
    if not article:
        raise ValueError("新聞來源不能是空白")
    load_local_env()
    api_key = os.environ.get("GEMINI_API_KEY", "")
    if mode == "ai":
        result = summarize_with_gemini(article, api_key, os.getenv("GEMINI_MODEL", MODEL_DEFAULT))
        source_mode = "AI 真實生成"
    elif mode == "demo":
        result = validate_result(demo_result())
        source_mode = "人工示範（非 AI 生成）"
    else:
        raise ValueError("模式只能是 ai 或 demo")
    document = {
        "mode": mode,
        "mode_label": source_mode,
        "model": os.getenv("GEMINI_MODEL", MODEL_DEFAULT) if mode == "ai" else "未呼叫模型",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "article": article,
        "result": result,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return document


def main() -> None:
    parser = argparse.ArgumentParser(description="AI 新聞摘要與靜態網站資料產生器")
    parser.add_argument("--mode", choices=["ai", "demo"], default="ai")
    parser.add_argument("--input", type=Path, default=INPUT)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    document = build(args.mode, args.input, args.output)
    print(f"成功產生 {args.output}｜{document['mode_label']}")
    print(json.dumps(document["result"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
