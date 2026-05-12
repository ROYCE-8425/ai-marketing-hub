"""
SpinEditor Auto Scraper — Cào dữ liệu THẬT từ SpinEditor tự động

Flow:
1. Dùng stored cookies + session token để gọi SpinEditor API
2. Parse HTML response để lấy keyword + search volume
3. Trả về structured data giống hệt SpinEditor

Nguồn: Dữ liệu THẬT từ SpinEditor (auto-scraped)
"""

import os
import re
import json
import asyncio
from typing import Any, Dict, List, Optional
from urllib.parse import quote_plus, urlencode
from datetime import datetime

import httpx
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"), override=True)

# SpinEditor session config file
SPIN_CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "spineditor_session.json")

# ── Session Management ───────────────────────────────────────────────────────


def load_spin_session() -> Dict[str, str]:
    """Load SpinEditor session from config file."""
    if os.path.exists(SPIN_CONFIG_PATH):
        with open(SPIN_CONFIG_PATH, "r") as f:
            return json.load(f)
    return {}


def save_spin_session(session: Dict[str, str]):
    """Save SpinEditor session to config file."""
    os.makedirs(os.path.dirname(SPIN_CONFIG_PATH), exist_ok=True)
    with open(SPIN_CONFIG_PATH, "w") as f:
        json.dump(session, f, indent=2)


# ── Step 1: Fetch SpinEditor page and extract tokens ─────────────────────────


async def _fetch_spin_page(cookies: str) -> Dict[str, str]:
    """
    Fetch SpinEditor keyword page and extract dynamic tokens.
    Returns: {apply_token, win_id, txt_id, btn_id}
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0",
        "Cookie": cookies,
        "Accept": "text/html,application/xhtml+xml",
    }
    
    async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
        resp = await client.get("https://spineditor.com/goi-y-tu-khoa", headers=headers)
        
        if resp.status_code != 200:
            raise ValueError(f"SpinEditor returned {resp.status_code} — cookies có thể đã hết hạn")
        
        html = resp.text
        
        # Check if logged in
        if "Đăng nhập" in html and "customerSession" not in cookies:
            raise ValueError("Chưa đăng nhập SpinEditor — cần cập nhật cookies")
        
        # Extract dynamic tokens
        tokens = {}
        
        # apply token — in page state
        apply_match = re.search(r'apply["\s:=]+["\']([A-Za-z0-9+/=]+)["\']', html)
        if apply_match:
            tokens["apply_token"] = apply_match.group(1)
        
        # Window ID
        win_match = re.search(r'(Window\d+_RD\d+)', html)
        if win_match:
            tokens["win_id"] = win_match.group(1)
        
        # Keyword input ID
        txt_match = re.search(r'(txtKeyword_RD\d+)', html)
        if txt_match:
            tokens["txt_id"] = txt_match.group(1)
        
        # Submit button ID
        btn_match = re.search(r'(btnSubmitKeyword_RD\d+)', html)
        if btn_match:
            tokens["btn_id"] = btn_match.group(1)
        
        # Also try generic patterns
        if "apply_token" not in tokens:
            apply_match2 = re.search(r'"apply":"([^"]+)"', html)
            if apply_match2:
                tokens["apply_token"] = apply_match2.group(1)
        
        tokens["page_html"] = html
        return tokens


# ── Step 2: Call SpinEditor DoAction API ─────────────────────────────────────


async def _call_spin_api(keyword: str, cookies: str, tokens: Dict[str, str]) -> str:
    """
    Call SpinEditor's internal AJAX endpoint to search keywords.
    Returns: HTML response with keyword data.
    """
    url = "https://spineditor.com/Code/Web/WebService.asmx/DoAction"
    
    win_id = tokens.get("win_id", "Window1_RD4867")
    txt_id = tokens.get("txt_id", "txtKeyword_RD4881")
    btn_id = tokens.get("btn_id", "btnSubmitKeyword_RD4884")
    apply_token = tokens.get("apply_token", "")
    
    # Build the form data exactly like SpinEditor sends it
    form_data = {
        "winId": win_id,
        "apply": apply_token,
        "m": "ReloadModel",
        f"{txt_id}": json.dumps({"ID": txt_id, "Value": keyword}),
        f"{btn_id}": json.dumps({"ID": btn_id}),
        "lang": "vi",
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0",
        "Cookie": cookies,
        "Content-Type": "application/x-www-form-urlencoded",
        "Referer": "https://spineditor.com/goi-y-tu-khoa",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://spineditor.com",
    }
    
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(url, data=form_data, headers=headers)
        
        if resp.status_code != 200:
            raise ValueError(f"SpinEditor API returned {resp.status_code}")
        
        return resp.text


# ── Step 3: Parse SpinEditor HTML response ───────────────────────────────────


def _parse_spin_keywords(html: str) -> List[Dict[str, Any]]:
    """
    Parse keyword data from SpinEditor HTML response.
    Extracts: keyword, search_volume, allintitle, search_results, kei, competition
    """
    keywords = []
    
    # Try JSON parsing first (DoAction might return JSON)
    try:
        data = json.loads(html)
        # If it's a JSON response, look for keyword data in the structure
        if isinstance(data, dict):
            html_content = data.get("d", data.get("html", data.get("Html", "")))
            if html_content:
                html = str(html_content)
    except (json.JSONDecodeError, TypeError):
        pass
    
    # Parse table rows — SpinEditor uses <tr> with keyword data
    # Pattern: <td>keyword</td><td>volume</td><td>allintitle</td>...
    row_pattern = re.compile(
        r'<tr[^>]*>\s*'
        r'(?:<td[^>]*>.*?</td>\s*)?'  # optional checkbox column
        r'<td[^>]*>\s*(?:<a[^>]*>)?\s*(.*?)\s*(?:</a>)?\s*</td>\s*'  # keyword
        r'<td[^>]*>\s*([\d,.\s]*|--|-|Đang xử lý)\s*</td>\s*'  # volume
        r'<td[^>]*>\s*([\d,.\s]*|--|-|Đang xử lý)\s*</td>\s*'  # allintitle
        r'<td[^>]*>\s*([\d,.\s]*|--|-|Đang xử lý)\s*</td>\s*'  # search results
        r'<td[^>]*>\s*([\d,.\s]*|--|-|Đang xử lý)\s*</td>\s*'  # kei
        r'<td[^>]*>\s*(Low|Medium|High|Very High|--|-|Đang xử lý)\s*</td>',  # competition
        re.IGNORECASE | re.DOTALL
    )
    
    for match in row_pattern.finditer(html):
        kw = re.sub(r'<[^>]+>', '', match.group(1)).strip()
        if not kw or kw.lower() in ('từ khóa', 'keyword'):
            continue
        
        def parse_num(s):
            s = s.strip().replace(',', '').replace('.', '')
            if s in ('--', '-', '', 'Đang xử lý'):
                return None
            try:
                return int(s)
            except ValueError:
                return None
        
        keywords.append({
            "keyword": kw,
            "search_volume": parse_num(match.group(2)),
            "allintitle": parse_num(match.group(3)),
            "total_results": parse_num(match.group(4)),
            "kei": parse_num(match.group(5)),
            "competition": match.group(6).strip() if match.group(6).strip() not in ('--', '-', 'Đang xử lý') else "--",
        })
    
    # Fallback: simpler pattern for just keyword + volume
    if not keywords:
        simple_pattern = re.compile(
            r'"Keyword"\s*:\s*"([^"]+)"\s*,\s*"SearchVolume"\s*:\s*([\d.]+)',
            re.IGNORECASE
        )
        for match in simple_pattern.finditer(html):
            kw = match.group(1).strip()
            vol = float(match.group(2))
            keywords.append({
                "keyword": kw,
                "search_volume": int(vol) if vol > 0 else None,
                "allintitle": None,
                "total_results": None,
                "kei": None,
                "competition": "--",
            })
    
    # Fallback 2: look for data in JavaScript arrays
    if not keywords:
        js_array = re.findall(r'\["([^"]+)",\s*([\d]+)', html)
        for kw, vol in js_array:
            keywords.append({
                "keyword": kw,
                "search_volume": int(vol) if vol != "0" else None,
                "allintitle": None,
                "total_results": None,
                "kei": None,
                "competition": "--",
            })
    
    return keywords


# ── Step 4: Fallback — scrape via page HTML ──────────────────────────────────


def _parse_spin_page_html(html: str) -> List[Dict[str, Any]]:
    """
    Parse keyword data directly from the full page HTML.
    This is used when we can load the page with keyword parameter.
    """
    keywords = []
    
    # Look for grid/table data in the page
    # SpinEditor renders keywords in a grid with class patterns
    td_pattern = re.compile(
        r'title="([^"]*)"[^>]*>([^<]*)</.*?'
        r'<td[^>]*>([\d,]*)</td>',
        re.DOTALL
    )
    
    # Also try extracting from JavaScript data embedded in page
    json_data = re.findall(r'"Keyword":"([^"]+)".*?"SearchVolume":([\d.]+)', html)
    for kw, vol in json_data:
        keywords.append({
            "keyword": kw,
            "search_volume": int(float(vol)) if float(vol) > 0 else None,
            "allintitle": None,
            "total_results": None,
            "kei": None,
            "competition": "--",
        })
    
    return keywords


# ── Main Function ────────────────────────────────────────────────────────────


async def scrape_spineditor(keyword: str) -> Dict[str, Any]:
    """
    Tự động cào dữ liệu từ SpinEditor.
    
    Cần cookies SpinEditor đã được lưu trong data/spineditor_session.json
    """
    session = load_spin_session()
    cookies = session.get("cookies", "")
    
    if not cookies:
        return {
            "error": "Chưa cấu hình SpinEditor session. Vào Settings → Nhập cookies SpinEditor.",
            "setup_required": True,
        }
    
    try:
        # Step 1: Fetch page and get tokens
        tokens = await _fetch_spin_page(cookies)
        
        # Step 2: Try direct page scraping first (faster)
        page_keywords = _parse_spin_page_html(tokens.get("page_html", ""))
        
        if not page_keywords and tokens.get("apply_token"):
            # Step 3: Call DoAction API
            api_response = await _call_spin_api(keyword, cookies, tokens)
            page_keywords = _parse_spin_keywords(api_response)
        
        if not page_keywords:
            # Step 4: Try loading page with keyword parameter
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                "Cookie": cookies,
            }
            async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
                resp = await client.get(
                    f"https://spineditor.com/goi-y-tu-khoa?keyword={quote_plus(keyword)}",
                    headers=headers,
                )
                if resp.status_code == 200:
                    page_keywords = _parse_spin_page_html(resp.text)
                    if not page_keywords:
                        page_keywords = _parse_spin_keywords(resp.text)
        
        return {
            "seed_keyword": keyword,
            "total_suggestions": len(page_keywords),
            "keywords": page_keywords,
            "checked_metrics": True,
            "data_source": "SpinEditor (auto-scraped)",
            "source_note": "📊 Dữ liệu THẬT từ SpinEditor — Cào tự động",
            "scraped_at": datetime.now().isoformat(),
        }
    
    except Exception as e:
        return {
            "error": f"Lỗi cào SpinEditor: {str(e)}",
            "seed_keyword": keyword,
            "total_suggestions": 0,
            "keywords": [],
            "source_note": f"❌ Lỗi: {str(e)}",
        }


async def save_spineditor_cookies(cookies: str) -> Dict[str, Any]:
    """Save SpinEditor cookies for auto-scraping."""
    session = {"cookies": cookies, "updated_at": datetime.now().isoformat()}
    save_spin_session(session)
    
    # Verify cookies work
    try:
        tokens = await _fetch_spin_page(cookies)
        has_tokens = bool(tokens.get("win_id"))
        return {
            "status": "ok",
            "message": "Cookies SpinEditor đã lưu thành công!",
            "verified": has_tokens,
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Cookies không hợp lệ: {str(e)}",
        }
