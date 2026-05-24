# AI Marketing Hub — Tài liệu Báo cáo Đồ án

> **Phiên bản**: v3.2.0 · Phase 20 | Cập nhật: 2026-05-24
> **Repo**: `ai-marketing-hub/`

---

## 1) Giới thiệu đề tài (1–3 phút)

### Thành viên
- **Trần Như Ý** — Phát triển toàn bộ hệ thống (Full-Stack Developer)

### Tên đề tài
**AI Marketing Hub** — Nền tảng AI-powered SEO & Marketing Automation cho thị trường Việt Nam

### Lý do chọn đề tài

- **Thị trường SEO Việt Nam** chưa có công cụ tích hợp toàn diện bằng tiếng Việt — đa phần SMEs phải dùng nhiều tool rời rạc (Ahrefs, Screaming Frog, Yoast…), tốn chi phí và thiếu đồng bộ dữ liệu.
- **AI generative (LLM)** đã đủ trưởng thành để hỗ trợ viết nội dung SEO, phân tích từ khóa, và tối ưu kỹ thuật — nhưng các tool hiện tại chưa khai thác cho thị trường tiếng Việt.
- **Mục tiêu**: Xây dựng một nền tảng **all-in-one**, vừa phân tích SEO kỹ thuật, vừa tạo nội dung AI, vừa quản lý chiến dịch marketing — tất cả bằng giao diện tiếng Việt.

### Điểm khác biệt so với phần mềm cùng loại

| Đặc điểm | AI Marketing Hub | Ahrefs / SEMrush | Yoast SEO |
|-----------|:---:|:---:|:---:|
| Giao diện hoàn toàn tiếng Việt | ✅ | ❌ | ❌ |
| AI viết nội dung SEO (Groq LLaMA 3.3) | ✅ | ❌ | ❌ |
| Content Humanizer (chống phát hiện AI) | ✅ | ❌ | ❌ |
| 12 loại Schema.org generator | ✅ | ❌ | Hạn chế |
| Tối ưu GEO (Generative Engine Optimization) | ✅ | ❌ | ❌ |
| CRO + Trust Signal analysis | ✅ | Hạn chế | ❌ |
| Multi-site management | ✅ | ✅ | ❌ |
| A/B Testing SEO content | ✅ | Hạn chế | ❌ |
| Open source / self-hosted | ✅ | ❌ | ❌ |
| Tích hợp GSC + GA4 + DataForSEO | ✅ | Riêng biệt | ❌ |

**Tóm lại**: Không có tool nào kết hợp cả 3 trục: **phân tích SEO kỹ thuật** + **tạo nội dung AI bằng tiếng Việt** + **quản lý chiến dịch marketing** trong một giao diện duy nhất.

---

## 2) Use Case + Diagrams (1–3 phút)

### Danh sách chức năng chính (Use Case)

**Nhóm 1 — Phân tích SEO** (8 chức năng):
1. **SEO Audit** — Kiểm tra on-page SEO, keyword density, chấm điểm A-F
2. **Technical SEO** — Scan 8 tiêu chí kỹ thuật (meta, heading, hình ảnh, mobile, links, sitemap, hiệu suất, bảo mật)
3. **Core Web Vitals** — Kiểm tra LCP, INP, CLS qua Google PageSpeed Insights API
4. **CRO & Trust Analysis** — CRO checklist, CTA analysis, trust signals, above-fold analysis
5. **SERP Live** — Tra cứu kết quả tìm kiếm trực tiếp (DuckDuckGo / DataForSEO)
6. **Backlink Analyzer** — Phân tích liên kết nội bộ/ngoại vi
7. **Broken Link Checker** — Quét link hỏng bất đồng bộ + health score
8. **Schema Validator** — Validate JSON-LD structured data, hỗ trợ 25+ loại schema

**Nhóm 2 — Từ khóa** (3 chức năng):
9. **Rank Tracker** — Theo dõi thứ hạng từ khóa, import CSV, sync GSC, alerts, export Excel
10. **AI Keyword Analysis** — Phân tích từ khóa AI (TF-IDF, KMeans clustering, GSC data)
11. **Competitor Gap Analysis** — So sánh nội dung đối thủ, tìm khoảng trống

**Nhóm 3 — Nội dung AI** (4 chức năng):
12. **AI Content Planner** — Lập outline, sections, meta tags bằng AI
13. **AI Article Writer** — Viết bài hoàn chỉnh bằng Groq LLaMA 3.3 70B
14. **Spin Editor** — Viết lại nội dung với 4 giọng văn, 3 mức độ, bảo toàn từ khóa
15. **Content Polish / Humanizer** — Xóa watermark AI, thay thế cụm từ AI, chấm điểm readability

**Nhóm 4 — Tối ưu & Schema** (2 chức năng):
16. **GEO Optimizer** — Tối ưu cho AI search engines (SGE, Perplexity), E-E-A-T analysis
17. **Schema.org Generator** — 12 loại schema (FAQ, LocalBusiness, Product, Article, Breadcrumb, Organization, WebSite, JobPosting, Event, HowTo, Video, Review)

**Nhóm 5 — Quản lý & Công cụ** (6 chức năng):
18. **Content Calendar** — Lịch nội dung CRUD, gợi ý chủ đề AI
19. **A/B Testing SEO** — So sánh 2 phiên bản title/content với AI evaluation
20. **Report Generator** — Báo cáo SEO toàn diện bằng AI
21. **Campaign Tracker** — Theo dõi chiến dịch, opportunity scoring 8 yếu tố
22. **File Converter** — Chuyển PDF/Word/Excel/PPT → Markdown
23. **Multi-site Manager** — Quản lý nhiều website, chuyển đổi ngữ cảnh

**Nhóm 6 — Hệ thống** (3 chức năng):
24. **Auth System** — Đăng ký/đăng nhập JWT, RBAC (admin/editor/viewer)
25. **WordPress Publisher** — Đẩy bài viết lên WordPress + Yoast SEO
26. **Usage History** — Ghi log toàn bộ API calls, thống kê sử dụng

### Diagram gợi ý

> 📌 Xem chi tiết tất cả diagram tại file **`OpenSpec/REPORT_DIAGRAMS.md`** (Mermaid format, copy trực tiếp vào slide).

---

## 3) Kịch bản Demo (5–7 phút)

### Chuẩn bị trước demo
```
✅ Backend chạy: http://localhost:8000
✅ Frontend chạy: http://localhost:5173
✅ Đã init database: python init_database.py
✅ Tài khoản test: admin@aimarketing.vn / admin123
✅ GROQ_API_KEY đã cấu hình (cho phần AI)
```

---

### Bước 1 — Đăng nhập (30 giây) 🔐

**Thao tác**: Mở `http://localhost:5173` → Tự chuyển sang `/login`

**Câu thoại gợi ý**:
> "Đầu tiên, hệ thống có xác thực JWT — phân quyền 3 cấp: Admin, Editor, Viewer. Em sẽ đăng nhập bằng tài khoản admin."

**Thao tác**:
- Nhập `admin@aimarketing.vn` / `admin123`
- Nhấn **Đăng nhập**
- Chỉ vào UserMenu ở góc phải → hiển thị tên + vai trò

> "Hệ thống dùng JWT access token + refresh token. Admin có quyền quản lý tất cả người dùng."

---

### Bước 2 — Dashboard tổng quan (30 giây) 📊

**Câu thoại**:
> "Sau khi đăng nhập, trang Dashboard hiển thị tổng quan: kết nối GSC, GA4, số liệu traffic. Sidebar bên trái chia thành 6 nhóm chức năng với 22 trang."

**Chỉ vào**: Sidebar → các nhóm: Phân tích SEO, Từ khóa, Nội dung, Công cụ, Quản lý

---

### Bước 3 — Core Web Vitals (45 giây) ⚡ `[ĐIỂM NHẤN]`

**Thao tác**: Click **Core Web Vitals** → Nhập URL: `https://binhphuocmitsubishi.com`

**Câu thoại**:
> "Phần Core Web Vitals gọi trực tiếp Google PageSpeed Insights API. Trả về 5 chỉ số: LCP, INP, CLS, FCP, TTFB — cùng Lighthouse scores cho Performance, SEO, Accessibility."

**Kết quả hiển thị**: Bảng điểm màu xanh/vàng/đỏ, danh sách opportunities cải thiện.

> "Đây là real-time data từ Google, không phải mock. Kết quả giống hệt PageSpeed Insights online."

**Plan B**: Nếu PageSpeed API lỗi → Nói: "API key có quota, demo kết quả đã cache" → chuyển sang chức năng khác.

---

### Bước 4 — SEO Audit (1 phút) 🔎

**Thao tác**: Click **Kiểm tra SEO** → Nhập URL bài viết + từ khóa → **Phân tích**

**Câu thoại**:
> "SEO Audit phân tích on-page SEO: keyword density, phân bố từ khóa (heatmap), từ khóa LSI, và chấm điểm tổng thể từ A đến F."

**Chỉ vào kết quả**:
- Score Ring (điểm tổng)
- Category Scores (thanh bar)
- Keyword Heatmap (phân bố trong bài)
- Critical Issues / Warnings / Suggestions

> "Hệ thống phân tích thật nội dung trang, trích xuất text qua BeautifulSoup, tính mật độ và phân bố từ khóa."

---

### Bước 5 — AI Content Writer (1.5 phút) ✍️ `[ĐIỂM NHẤN CHÍNH]`

**Thao tác**: Click **Viết nội dung AI** → Nhập từ khóa "mitsubishi xpander 2026" + đối tượng "khách hàng mua xe gia đình"

**Câu thoại**:
> "Đây là phần em cho là đặc sắc nhất. AI Content Planner dùng Groq LLaMA 3.3 70B để tạo outline bài viết — bao gồm tiêu đề, dàn ý chi tiết, engagement map, meta SEO."

**Sau khi có outline**, cuộn xuống:
> "Mỗi section có chiến lược tiếp cận riêng, hook, knowledge gaps phải đề cập, và CTA. Em có thể bấm 'Viết toàn bộ bài' để AI sinh content cho từng phần."

**Nếu GROQ_API_KEY không có / lỗi**:
> "Phần AI cần Groq API key. Nếu key hết quota, hệ thống trả về error rõ ràng thay vì crash."

---

### Bước 6 — Content Humanizer (45 giây) 🧹 `[ĐIỂM NHẤN]`

**Thao tác**: Click **Spin Editor** hoặc vào endpoint `/api/content/polish`

**Câu thoại**:
> "Sau khi AI viết bài, Content Humanizer xử lý bài viết qua pipeline 3 bước:
> 1. **ContentScrubber**: Xóa watermark Unicode ẩn (zero-width spaces, BOM), thay cụm từ AI ('It's important to note...')
> 2. **ReadabilityScorer**: Chấm điểm Flesch Reading Ease
> 3. **EngagementAnalyzer**: Đánh giá hook, nhịp đọc, phân bố CTA
> 
> Kết quả: nội dung 'sạch' hơn, khó bị phát hiện là AI-generated."

---

### Bước 7 — GEO Optimizer + Schema Generator (1 phút) 🧠

**Thao tác**: Click **Tối ưu GEO** → Chọn tab **FAQ Schema** → Nhập URL

**Câu thoại**:
> "GEO Optimizer giúp tối ưu cho AI search engines mới như Google SGE, Bing Chat, Perplexity. Phần Schema Generator có 12 loại schema — em demo FAQ Schema."

**Thao tác**: Nhập URL → AI tự tạo câu hỏi/trả lời từ nội dung trang → Output JSON-LD

> "Kết quả là JSON-LD chuẩn Schema.org, copy paste trực tiếp vào HTML. Ngoài FAQ còn có: LocalBusiness, Product, Article, Event, HowTo, Video, Review..."

**Nếu Groq lỗi**: Chuyển sang demo **LocalBusiness Schema** (không cần AI, chỉ cần nhập form thông tin).

---

### Bước 8 — Rank Tracker (45 giây) 📍

**Thao tác**: Click **Theo dõi Keyword**

**Câu thoại**:
> "Rank Tracker theo dõi vị trí từ khóa theo thời gian. Dữ liệu sample 30 ngày với 10 từ khóa được tạo sẵn qua init_database.py. Có thể import CSV, sync từ GSC, đặt alert khi tụt hạng, export Excel."

**Chỉ vào**: Biểu đồ đường (recharts), bảng keywords, filter theo tag.

---

### Bước 9 — Multi-site Manager (30 giây) 🏢

**Thao tác**: Click **Multi-site** → Thêm site mới (nếu cần)

**Câu thoại**:
> "Hệ thống hỗ trợ quản lý nhiều website. Chuyển đổi site ảnh hưởng toàn bộ: Rank Tracker, Content Calendar, A/B Testing đều filter theo site đang active."

---

### Bước 10 — Kết thúc demo (30 giây)

**Câu thoại**:
> "Ngoài ra còn có: Broken Link Checker, Schema Validator, Competitor Analysis, Content Calendar, A/B Testing, File Converter, Report Generator — tổng cộng 22 trang, 99 API endpoints."

**Mở nhanh**: `/broken-links` hoặc `/schema-validator` để chứng minh giao diện hoạt động.

---

### Plan B — Xử lý lỗi khi demo

| Tình huống | Xử lý |
|------------|--------|
| **Groq API hết quota / lỗi mạng** | Demo phần không cần AI: CWV, Broken Links, Schema Validator, Rank Tracker, Multi-site |
| **PageSpeed API lỗi** | Nói "API có rate limit" → chuyển demo chức năng khác |
| **Backend không start** | Kiểm tra `python init_database.py` trước, rồi start lại |
| **Frontend lỗi** | Chạy `npx tsc -b` trước demo để verify, mở DevTools kiểm tra |
| **Mạng chậm / mất** | Rank Tracker, Content Calendar, Multi-site Manager đều hoạt động offline (SQLite local) |

---

## 4) Kết luận + Hướng phát triển (1 phút)

### Kết quả đạt được

- ✅ Xây dựng **nền tảng SEO & Marketing all-in-one** với 22 trang, 99 API endpoints, ~35,000 LOC
- ✅ Tích hợp **AI generative (Groq LLaMA 3.3 70B)** cho 5 chức năng: viết bài, lập outline, spin, phân tích từ khóa, đề xuất chủ đề
- ✅ **Content Humanizer** pipeline 3 bước — tính năng độc đáo, chưa có tool nào tương tự
- ✅ **12 loại Schema.org generator** — nhiều hơn hầu hết các plugin SEO
- ✅ **Real-time data integration**: Google Search Console, GA4, PageSpeed Insights, DataForSEO
- ✅ **Auth system** hoàn chỉnh: JWT + refresh token + RBAC (admin/editor/viewer)
- ✅ **Kiến trúc sạch**: React 19 SPA + FastAPI backend, vanilla CSS dark glassmorphism, 6 SQLite databases
- ✅ **Docker** containerization, CI/CD pipeline

### Hạn chế hiện tại

- Chưa có unit test coverage (0%) → ảnh hưởng maintainability
- Chưa có API rate limiting → rủi ro abuse khi deploy public
- SQLite chỉ phù hợp single-user / development → cần migrate PostgreSQL cho production
- Chưa có email notification cho alerts
- Một số chức năng phụ thuộc API key bên ngoài (Groq, PageSpeed, DataForSEO)

### Hướng phát triển tiếp theo (ĐACN/ĐATN)

1. **PostgreSQL migration** — Multi-user, concurrent access, better performance
2. **Unit test coverage > 80%** — pytest (backend), Vitest (frontend)
3. **API rate limiting** — Token bucket per user, prevent abuse
4. **Email notifications** — Alert khi keyword tụt hạng, content đến hạn publish
5. **Mobile responsive app** — React Native hoặc PWA
6. **Multilingual support** — Mở rộng ra thị trường Đông Nam Á (Thái, Indo, Mã Lai)
7. **AI model upgrade** — Hỗ trợ nhiều model (Gemini, Claude) ngoài Groq
8. **Real-time collaboration** — WebSocket cho team editing
9. **Automated SEO monitoring** — Cron job scan định kỳ, so sánh trend

---

## Phụ lục — Thống kê kỹ thuật

### Tech Stack

| Layer | Công nghệ |
|-------|-----------|
| Frontend | React 19 + TypeScript 6 + Vite 8 |
| Styling | Vanilla CSS (dark glassmorphism) |
| Charts | Recharts |
| SEO | react-helmet-async, JSON-LD, OpenGraph |
| Backend | FastAPI + Python 3.13 + Uvicorn |
| AI Engine | Groq LLaMA 3.3 70B |
| Database | SQLite × 6 |
| Auth | JWT (bcrypt + python-jose) |
| HTTP Client | httpx (async) |
| HTML Parser | BeautifulSoup4 |
| ML | scikit-learn (KMeans clustering) |
| DevOps | Docker, GitHub Actions |

### Database Schema (6 databases)

| Database | Tables | Mô tả |
|----------|--------|--------|
| `auth.db` | users, refresh_tokens | JWT auth, RBAC |
| `sites.db` | managed_sites | Multi-site management |
| `rank_tracker.db` | tracked_keywords, ranking_history | Theo dõi thứ hạng |
| `content_calendar.db` | content_items | Lịch nội dung |
| `ab_tests.db` | ab_tests | A/B Testing SEO |
| `data/usage_history.db` | usage_log | API call logging |

### Số liệu dự án

| Metric | Giá trị |
|--------|---------|
| Tổng LOC | ~35,000+ |
| Frontend components | 37 files |
| Backend routers | 15 files |
| Backend core modules | 50 files |
| Custom React hooks | 6 |
| API endpoints | 99 |
| Routing pages | 22 |
| SQLite databases | 6 |
| Schema.org types | 12 |

