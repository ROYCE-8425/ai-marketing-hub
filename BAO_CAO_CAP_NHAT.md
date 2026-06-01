# BÁO CÁO CẬP NHẬT: Refactor Logic Chấm Điểm SEO/GEO

**Ngày:** 26/05/2026  
**Tác giả:** AI Project Manager (Antigravity)  
**Dự án:** AI Marketing Hub v3.2.0  
**Commit:** `819a5a2`

---

## 1. Mục tiêu

Sửa lại logic chấm điểm SEO và GEO để:
- Kết quả đúng về mặt kỹ thuật (dùng DOM thật thay vì regex markdown)
- Defend được về mặt kỹ thuật (mỗi điểm đều chỉ ra nguồn dữ liệu)
- Tách rõ giữa `measured fact`, `rule-based audit`, và `heuristic`

---

## 2. Vấn đề đã xác nhận từ code gốc

### 2.1. SEO Audit chấm sai bản chất cho live page

| Vấn đề | File | Dòng | Chi tiết |
|--------|------|------|----------|
| H1/H2/H3 parse bằng markdown regex | `seo_quality_rater.py` | 169-171 | `re.match(r'^#\s+', line)` — KHÔNG phải HTML |
| Links đếm bằng markdown syntax | `seo_quality_rater.py` | 451-454 | `re.findall(r'\[...\]\(http...')` |
| Sections chia sai | `keyword_analyzer.py` | 186-188 | Parse `# heading` thay vì `<h1>` |
| List detection sai | `seo_quality_rater.py` | 523-524 | Tìm `- ` markdown thay vì `<ul>/<ol>` |
| Meta description KHÔNG được truyền | `api_seo.py` | 44-49 | Luôn `-40 điểm` vì thiếu meta description |
| Word count lẫn noise | `api_seo.py` | 275 | `get_text()` gộp cả menu, footer, button text |

**Root cause:** `audit-url` fetch HTML thật → `soup.get_text()` → plain text → đưa vào scorer thiết kế cho markdown.

### 2.2. GEO score cộng điểm ảo

| Logic | Dòng | Điểm cộng | Vấn đề |
|-------|------|-----------|--------|
| Có domain thật | 219 | +5 | Mọi website đều có |
| Keyword trong domain | 225 | +5 | EMD không phải indicator chính |
| HTTPS | 232 | +3 | ~95% websites dùng HTTPS |
| "Base score cho có website" | 237 | +7 | Cộng free 7 điểm |

→ Bất kỳ URL nào cũng tự động được **20/100 điểm** mà không cần content tốt.

### 2.3. Hardcoded guidelines cho mọi loại trang

- `min_word_count: 2000` — homepage thường chỉ 200-500 từ
- `min_h2_sections: 4` — product page chỉ cần 2
- `min_external_links: 2` — homepage hiếm khi link ngoài

---

## 3. Giải pháp đã triển khai

### 3.1. Module mới: `html_page_parser.py` (Phase 1)

**File:** `backend/core/html_page_parser.py`  
**Mục đích:** Parse HTML DOM thành structured facts — KHÔNG scoring, KHÔNG heuristic.

Dataclass `PageFeatures` chứa:
- **Metadata:** `<title>`, `<meta name="description">`, canonical, noindex, Open Graph
- **Headings:** `<h1>`, `<h2>`, `<h3>` — parse trực tiếp từ DOM
- **Links:** `<a href>` — phân loại internal/external/nofollow
- **Content:** visible text (đã loại nav/footer/script/aside)
- **Media:** `<img>` alt text, lazy loading, video
- **Schema:** JSON-LD `<script type="application/ld+json">`
- **Technical:** viewport, HTTPS, lang attribute

**Page type detection** (heuristic duy nhất, có confidence label):
- Schema-based: `Product` → product page (high confidence)
- URL pattern: `/blog/`, `/san-pham/`, `/dich-vu/` (medium confidence)
- Content-based: word count + H2 count (low confidence)

### 3.2. SEO Scorer refactored (Phase 2)

**File:** `backend/core/seo_quality_rater.py` — thêm function `rate_page_seo()`

#### 8 categories mới (100 điểm tổng):

| # | Category | Max | Nguồn dữ liệu |
|---|----------|-----|---------------|
| 1 | Indexability & Crawlability | 20 | **Measured** (noindex, canonical, HTTPS) |
| 2 | Metadata | 15 | **Rule-based** (title/desc length + keyword) |
| 3 | Heading & Content Structure | 15 | **Measured** (H1/H2/H3 from DOM) |
| 4 | Content Quality On-page | 15 | **Rule-based** (word count, lists, tables) |
| 5 | Keyword Targeting | 10 | **Rule-based** (density, placement) |
| 6 | Internal/External Linking | 10 | **Measured** (`<a>` tags from DOM) |
| 7 | Media & Accessibility | 5 | **Measured** (img alt, video) |
| 8 | Technical UX Signals | 10 | **Measured** (viewport, lang, OG) |

#### Page-type-aware guidelines:

| Page type | Min words | Min H2 | Min internal links |
|-----------|-----------|--------|-------------------|
| Homepage | 150 | 1 | 5 |
| Article | 1200 | 3 | 3 |
| Product | 200 | 1 | 2 |
| Service | 400 | 2 | 3 |
| Listing | 50 | 0 | 5 |

#### Response mới thêm:
- `page_type`: loại trang được phát hiện
- `page_type_confidence`: "high" | "medium" | "low"
- `confidence`: mức độ tin cậy tổng
- `category_max`: điểm tối đa mỗi category
- `data_sources`: "measured" | "rule_based" cho mỗi category

### 3.3. GEO → AI Search Readiness (Phase 3)

**File:** `backend/core/geo_analyzer.py`

#### Thay đổi chính:
1. **Xóa điểm ảo:** domain (+5), keyword domain (+5), HTTPS (+3), base website (+7) → chuyển thành `context_signals` (thông tin, không tính điểm)
2. **Đổi tên:** `geo_score` → `readiness_score`, thêm `score_type: "heuristic_readiness"`
3. **Thêm category mới:** `answer_extraction_readiness` — kiểm tra Q&A format, definitions, step-by-step content

#### 5 categories mới (100 điểm tổng):

| # | Category | Max | Type |
|---|----------|-----|------|
| 1 | Structured Data Quality | 25 | **Deterministic** |
| 2 | Content Structure for AI | 20 | **Deterministic** |
| 3 | E-E-A-T Clarity | 20 | **Mixed** |
| 4 | Answer Extraction Readiness | 20 | **Heuristic** |
| 5 | Media & Corroboration | 15 | **Deterministic** |

#### Backward compat:
- `geo_score` vẫn được trả về (= `readiness_score`) để frontend cũ không bị break

### 3.4. Endpoint `audit-url` cập nhật (Phase 2)

**File:** `backend/routers/api_seo.py`

Flow mới:
1. Fetch HTML (giữ nguyên)
2. Parse HTML → `PageFeatures` (dùng `html_page_parser`)
3. Score SEO từ `PageFeatures` (dùng `rate_page_seo`)
4. Keyword analysis trên visible text (giữ nguyên)
5. CRO analysis trên visible text (giữ nguyên)

> **Lưu ý:** Endpoint `audit-seo` (chấm raw text/markdown) giữ nguyên logic cũ — đó là đúng use case cho pre-publish article.

---

## 4. Phân loại dữ liệu hiện tại

### 4.1. Deterministic (Đo lường thật)

| Metric | Nguồn |
|--------|-------|
| H1/H2/H3 count và text | DOM `<h1>`, `<h2>`, `<h3>` |
| Internal/External link count | DOM `<a href>` |
| Image alt text ratio | DOM `<img alt>` |
| Meta title/description | DOM `<title>`, `<meta name="description">` |
| Canonical URL | DOM `<link rel="canonical">` |
| HTTPS | URL scheme |
| Viewport | DOM `<meta name="viewport">` |
| Schema.org types | DOM `<script type="application/ld+json">` |
| Lists/Tables presence | DOM `<ul>`, `<ol>`, `<table>` |

### 4.2. Rule-based (Quy tắc rõ ràng)

| Rule | Mô tả |
|------|-------|
| Title length 30-65 chars | Theo Google SERP display limits |
| Description length 80-165 chars | Theo Google snippet limits |
| Keyword in title/H1/first-100-words | Best practice SEO on-page |
| Word count by page type | Varies by type (homepage 150, article 1200) |
| Keyword density < 3% | Anti-stuffing threshold |

### 4.3. Heuristic (Ước lượng)

| Metric | Mô tả | Confidence |
|--------|-------|-----------|
| Page type detection | Dựa trên URL + schema + content signals | Low-High |
| Q&A readiness | Tìm pattern "hỏi:", "đáp:", definitions | Low |
| E-E-A-T clarity | Trust words, author meta, date tags | Medium |
| AI citation friendliness | Paragraph length, ordered lists | Low |

---

## 5. Files đã sửa

| File | Thay đổi |
|------|----------|
| `backend/core/html_page_parser.py` | **MỚI** — DOM parser, 280 lines |
| `backend/core/seo_quality_rater.py` | Thêm `rate_page_seo()` + `GUIDELINES_BY_PAGE_TYPE` |
| `backend/core/geo_analyzer.py` | Xóa `_check_ai_visibility()`, thêm `_check_ai_citation_readiness()`, refactor `analyze_geo()` |
| `backend/routers/api_seo.py` | `audit-url` dùng `parse_html_page` + `rate_page_seo` |
| `frontend/src/types/seo.ts` | Thêm optional fields cho v2 response |

---

## 6. Verification

| Check | Kết quả |
|-------|---------|
| `python -B -c "from core.html_page_parser import parse_html_page"` | ✅ OK |
| `python -B -c "from core.seo_quality_rater import rate_page_seo"` | ✅ OK |
| `python -B -c "from main import app"` | ✅ OK |
| `npx tsc -p tsconfig.app.json --noEmit` | ✅ OK |
| Backward compat `audit-seo` endpoint | ✅ Giữ nguyên |
| Backward compat `geo_score` field | ✅ Vẫn trả về |

---

## 7. So sánh trước/sau

### SEO Score

| Metric | Trước | Sau |
|--------|-------|-----|
| H1/H2/H3 source | Markdown regex `^# ` | DOM `<h1>`, `<h2>` |
| Link counting | `\[text\]\(url\)` regex | DOM `<a href>` tags |
| Meta description | **KHÔNG được truyền** (-40 free) | Parse từ `<meta name="description">` |
| Word count | Plain text (gồm menu/footer) | Visible text (loại nav/footer/script) |
| Page type | Hardcoded 2000 words cho mọi trang | 6 page types với guidelines riêng |
| Data source label | Không có | Mỗi category có `measured/rule_based` |

### GEO Score

| Metric | Trước | Sau |
|--------|-------|-----|
| Score name | `geo_score` | `readiness_score` + `score_type: "heuristic_readiness"` |
| Free points | +20 (domain + HTTPS + base) | 0 (chuyển vào `context_signals`) |
| AI Visibility | Dựa trên domain/HTTPS | `answer_extraction_readiness` — Q&A, definitions |
| Category labels | Không có | `deterministic / heuristic / mixed` |
| Weights | 5×20 = 100 | 25+20+20+20+15 = 100 |

---

## 8. Hạn chế đã biết

1. **Keyword density** vẫn dựa trên visible text (có thể lẫn text từ sidebar) — cải thiện cần JS rendering
2. **Page type detection** low confidence khi không có Schema.org hoặc URL pattern rõ ràng
3. **E-E-A-T scoring** vẫn là heuristic (tìm trust words) — cải thiện cần NLP/AI
4. **`audit-seo` endpoint** vẫn dùng markdown parser cũ — đây là **đúng** vì nó chấm raw article text pre-publish

---

*Báo cáo được tạo tự động bởi AI Project Manager.*
