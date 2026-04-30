# ⚠️ DANH SÁCH DỮ LIỆU GIẢ (MOCK DATA) TRONG DỰ ÁN

> **Mục tiêu:** Chuyển tất cả từ mock → real data  
> **Ngày cập nhật:** 30/04/2026

---

## 🔴 CẦN SỬA NGAY (Đang hiển thị dữ liệu giả cho user)

### 1. Google Analytics 4 — `core/ga4_fetcher.py`
**Vấn đề:** Toàn bộ dữ liệu GA4 là MOCK — random numbers
| Dòng | Hàm mock | Dữ liệu giả |
|------|----------|-------------|
| 67-96 | `fetch_ga4_data()` | Trả về `"data_source": "mock"` khi không có GA4 credentials |
| 237 | `_mock_overview()` | Sessions: 1247, Users: 892, Pageviews: 3421 (cố định) |
| 248 | `_mock_traffic_sources()` | Organic: 523, Direct: 234, Social: 156 (cố định) |
| 257 | `_mock_top_pages()` | 3 trang giả với views/duration cố định |
| 266 | `_mock_daily_sessions()` | Random Gaussian sessions 30 ngày (`random.gauss(40, 12)`) |

**Cách fix:** Cài `google-analytics-data` + tạo Service Account → truyền `GA4_CREDENTIALS_PATH`

---

### 2. Google Search Console — `core/google_search_console.py`  
**Vấn đề:** Module cần `googleapiclient` nhưng chưa cài → hoàn toàn không hoạt động
| Dòng | Vấn đề |
|------|--------|
| Import | `from googleapiclient` → **ModuleNotFoundError** |
| Toàn bộ | Không thể fetch keywords, clicks, impressions, positions |

**Cách fix:** `pip install google-api-python-client google-auth` + OAuth2 setup

---

### 3. Data Router — `routers/api_data.py`
**Vấn đề:** 3 hàm mock data fallback khi không có API credentials
| Dòng | Hàm mock | Dữ liệu giả |
|------|----------|-------------|
| 249 | `_mock_gsc_data()` | Position: random 5-45, Impressions: random, CTR: random |
| 269 | `_mock_ga4_data()` | Sessions: 847, Users: 623, Bounce: 42.3% (cố định) |
| 283 | `_mock_serp_data()` | Search volume, CPC, difficulty giả theo intent |

**Nơi gọi mock:**
- Dòng 476-504: GSC sync → fallback mock khi OAuth fail
- Dòng 513-515: GA4 sync → fallback mock
- Dòng 561-567: SERP sync → fallback mock khi DataForSEO không có key

---

### 4. SERP Scraper — `core/google_serp_scraper.py`
**Vấn đề:** Có hàm `_mock_serp()` trả dữ liệu SERP giả bằng tiếng Việt
| Dòng | Hàm mock | Dữ liệu giả |
|------|----------|-------------|
| 35 | `_mock_serp()` | 3 results cố định với URLs giả |
| 113 | `search_google()` | Fallback mock khi DuckDuckGo fail |

**Hiện trạng:** DuckDuckGo search **hoạt động real** → mock chỉ là fallback

---

### 5. AI Keyword Analyzer — `core/ai_keyword_analyzer.py`
**Vấn đề:** Trả `"data_source": "mock"` khi Groq API fail
| Dòng | Vấn đề |
|------|--------|
| 302 | Fallback mock data khi AI call thất bại |

**Hiện trạng:** Groq API key **đã cấu hình** → chỉ mock khi API down

---

## 🟡 MOCK NHẸ (Sample data trong code, không ảnh hưởng production)

### 6. Sample content trong `if __name__ == "__main__"`
Các file này chứa sample content chỉ dùng khi chạy trực tiếp file (testing):
- `readability_scorer.py:466` — sample_content cho test
- `cta_analyzer.py:500` — sample_content cho test  
- `cro_checker.py:592` — sample_content cho test
- `landing_page_scorer.py:701` — sample_content cho test
- `keyword_analyzer.py:612` — sample_content cho test
- `trust_signal_analyzer.py:521` — sample_content cho test
- `above_fold_analyzer.py:458` — sample_content cho test
- `seo_quality_rater.py:595` — sample_content cho test

**→ KHÔNG cần sửa** — đây là test code, không chạy trong production

---

## 🟢 ĐÃ REAL (Không có mock)

| Module | Trạng thái | Ghi chú |
|--------|-----------|---------|
| SEO Audit (`seo_quality_rater.py`) | ✅ Real | Phân tích content thật |
| Keyword Analyzer (`keyword_analyzer.py`) | ✅ Real | TF-IDF + KMeans clustering |
| CRO Checker (`cro_checker.py`) | ✅ Real | Rule-based analysis |
| CTA Analyzer (`cta_analyzer.py`) | ✅ Real | Pattern matching |
| Trust Signals (`trust_signal_analyzer.py`) | ✅ Real | Pattern matching |
| Above Fold (`above_fold_analyzer.py`) | ✅ Real | Content analysis |
| Technical SEO (`technical_seo.py`) | ✅ Real | Scrape + analyze |
| Backlink Analyzer (`backlink_analyzer.py`) | ✅ Real | Scrape links |
| Spin Editor (`spin_editor.py`) | ✅ Real | Groq AI |
| GEO Optimizer (`geo_analyzer.py`) | ✅ Real | Groq AI |
| A/B Testing (`ab_testing.py`) | ✅ Real | Groq AI + SQLite |
| Report Generator (`report_generator.py`) | ✅ Real | Groq AI |
| Content Calendar (`content_calendar.py`) | ✅ Real | SQLite CRUD |
| Site Manager (`site_manager.py`) | ✅ Real | SQLite CRUD |
| Rank Tracker (`rank_tracker.py`) | ✅ Real | SQLite + GSC sync |
| File Converter (`file_converter.py`) | ✅ Real | MarkItDown |
| WordPress Publisher (`wordpress_publisher.py`) | ✅ Real | WP REST API |
| Competitor Gap (`competitor_gap_analyzer.py`) | ✅ Real | Scrape + analyze |
| Article Planner (`article_planner.py`) | ✅ Real | Rule-based |
| Content Scorer (`content_scorer.py`) | ✅ Real | Multi-algorithm |
| SERP Live (DuckDuckGo) | ✅ Real | duckduckgo-search |
| DataForSEO (`dataforseo.py`) | ⚠️ Cần API key | Đã code xong |

---

## 📋 TÓM TẮT

| Loại | Số lượng | Cần làm |
|------|---------|---------|
| 🔴 Mock data chính | **5 modules** | Cần API keys + cài thêm libs |
| 🟡 Sample test data | 8 files | Không cần sửa |
| 🟢 Real data | **22 modules** | Đã hoạt động |

### Để chuyển 100% sang REAL, cần:
1. `pip install google-api-python-client google-auth google-analytics-data`
2. Tạo Google Cloud Project → bật GSC API + GA4 API
3. Tạo OAuth2 credentials → lấy refresh token
4. Tạo GA4 Service Account → download JSON key
5. (Tùy chọn) Đăng ký DataForSEO → lấy login/password

---

*File được tạo để tracking mock data — cập nhật khi có thay đổi*
