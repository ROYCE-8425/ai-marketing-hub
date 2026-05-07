# ⚠️ MOCK DATA STATUS — AI Marketing Hub

> **Chính sách:** KHÔNG có mock/dummy/synthetic data trong user-facing flows.
> **Ngày cập nhật:** 05/05/2026 · v3.2.0 · Phase 20c (multi-site hardened)

---

## 🟢 REAL DATA — 23+ modules

Tất cả modules sau trả dữ liệu thật (scrape, analyze, AI, database):

| Module | File | Loại |
|--------|------|------|
| SEO Audit | `seo_quality_rater.py` | Content analysis |
| Technical SEO | `technical_seo.py` | Scrape + analyze |
| CRO Checker | `cro_checker.py` | Rule-based |
| CTA Analyzer | `cta_analyzer.py` | Pattern matching |
| Trust Signals | `trust_signal_analyzer.py` | Pattern matching |
| Above Fold | `above_fold_analyzer.py` | Content analysis |
| Keyword Analyzer | `keyword_analyzer.py` | TF-IDF + KMeans |
| AI Keywords | `ai_keyword_analyzer.py` | GSC real + AI (Groq/Gemini) |
| Backlinks | `backlink_analyzer.py` | Scrape links |
| Competitor Gap | `competitor_gap_analyzer.py` | Scrape + analyze |
| Article Planner | `article_planner.py` | Rule-based |
| Content Scorer | `content_scorer.py` | Multi-algorithm |
| Spin Editor | `spin_editor.py` | Groq AI |
| GEO Optimizer | `geo_analyzer.py` | Groq AI + Schema |
| A/B Testing | `ab_testing.py` | Groq AI + SQLite |
| Report Generator | `report_generator.py` | Groq AI |
| Content Calendar | `content_calendar.py` | SQLite CRUD |
| Site Manager | `site_manager.py` | SQLite CRUD |
| Rank Tracker | `rank_tracker.py` | SQLite + GSC sync |
| File Converter | `file_converter.py` | MarkItDown |
| WordPress Publisher | `wordpress_publisher.py` | WP REST API |
| Google Search Console | `google_search_console.py` | httpx + OAuth2 |
| SERP Live | `google_serp_scraper.py` | DataForSEO (ưu tiên) hoặc Google Custom Search API |

---

## 🔴 CẦN CREDENTIALS — 3 connectors

Khi thiếu credentials, trả **error state** (không trả dữ liệu giả):

| Connector | Cần gì | Khi thiếu |
|-----------|--------|-----------|
| **GA4** | `GA4_PROPERTY_ID` + OAuth2 scope `analytics.readonly` | `error: "GA4_PROPERTY_ID chưa được cấu hình..."`, `data_source: "error"` |
| **DataForSEO** | `DATAFORSEO_LOGIN` + `DATAFORSEO_PASSWORD` | Thiếu key: `source: "missing_credentials"`. Có key nhưng lỗi: `source: "api_error"` |
| **Google Custom Search** | `GOOGLE_CUSTOM_SEARCH_API_KEY` + `GOOGLE_CUSTOM_SEARCH_ENGINE_ID` | Thiếu key: fallthrough sang error. Có key nhưng lỗi: `source: "api_error"` |
| **SERP Live** | Cần ít nhất 1 trong DataForSEO hoặc Custom Search | `source: "missing_credentials"`, hiển thị banner cần cấu hình |
| **GSC (OAuth flow)** | `GOOGLE_SEARCH_CONSOLE_CLIENT_ID/SECRET/REFRESH_TOKEN` | `source: "error"` |

### Hành vi khi thiếu credentials

**Backend:**
- Trả `{ "error": "...", "source": "error" }` hoặc `{ "source": "missing_credentials" }` hoặc `{ "source": "api_error" }`
- KHÔNG trả số liệu giả (clicks, impressions, sessions, etc.)
- Các section lỗi trả mảng rỗng `[]` hoặc object rỗng `{}`

**Frontend:**
- Banner cảnh báo rõ ràng (đỏ/vàng) với error message từ backend
- Charts hiển thị "Chưa có dữ liệu GA4" hoặc error chi tiết
- Campaign Tracker KHÔNG điền số giả vào form khi thiếu dữ liệu

---

## ❌ ĐÃ LOẠI BỎ (từ Phase 20 cleanup)

| Hàm đã xóa | File | Lý do |
|------------|------|-------|
| `_mock_overview()` | `ga4_fetcher.py` | Trả sessions/users cố định giả |
| `_mock_traffic_sources()` | `ga4_fetcher.py` | Trả source data cố định giả |
| `_mock_top_pages()` | `ga4_fetcher.py` | Trả page data cố định giả |
| `_mock_daily_sessions()` | `ga4_fetcher.py` | Trả random Gaussian sessions giả |
| `_mock_gsc_data()` | `api_data.py` | Trả position/clicks/impressions giả |
| `_mock_ga4_data()` | `api_data.py` | Trả pageviews/sessions cố định giả |
| `_mock_serp_data()` | `api_data.py` | Trả search volume/difficulty giả |
| `_mock_serp()` | `google_serp_scraper.py` | Trả 10 fake SERP results bằng tiếng Việt |
| `_buildDummyBulk()` | `useAutoFill.ts` | Frontend tự tạo bulk data giả khi fetch fail |

---

## 📋 TÓM TẮT

| Loại | Số lượng |
|------|---------|
| 🟢 Real data modules | **23+** |
| 🔴 Cần credentials | **3** (GA4, DataForSEO, GSC OAuth) |
| ❌ Mock functions đã xóa | **9** |
| ⚠️ Remaining test-only samples | 8 files (`if __name__ == "__main__"`) — không ảnh hưởng production |

---

*Cập nhật: 05/05/2026 — Multi-site hardening, DataForSEO error semantics, empty-site guards*
