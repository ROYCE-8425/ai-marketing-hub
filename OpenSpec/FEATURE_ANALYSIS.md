# AI Marketing Hub — Phân tích chi tiết từng chức năng

> **Mục đích:** Tài liệu mô tả chi tiết từng chức năng UI, API, data flow để AI agent phân tích mà không cần truy cập trình duyệt.
> **Phiên bản:** v3.2.0 — Production deployed tại trannhuy.online
> **Cập nhật:** 2026-05-26

---

## 1. Trang Đăng nhập (`/login`)

**Component:** `AuthPage.tsx`

### UI Elements
- Logo + tiêu đề "AI Marketing Hub"
- Tab chuyển đổi: Đăng nhập | Đăng ký
- Form đăng nhập: Email, Mật khẩu, nút "Đăng nhập"
- Link "Quên mật khẩu?"
- Nút "Đăng nhập với tên Ý" (Google OAuth — hiển thị email đã liên kết)
- Giao diện: Light card trên nền gradient nhạt

### API
- `POST /api/auth/login` → `{ email, password }` → `{ access_token, refresh_token, user }`
- `POST /api/auth/register` → `{ email, full_name, password }`
- Google OAuth: `GET /auth/google/login` → redirect Google → callback

### Trạng thái
- ✅ Đăng nhập email/password: Hoạt động
- ✅ Đăng ký: Hoạt động
- ✅ Google OAuth: Hoạt động (trannhuy8425@gmail.com)
- ✅ JWT token + refresh token
- ✅ Role-based: admin, editor, viewer

### Tài khoản test
| Email | Password | Role |
|-------|----------|------|
| admin@aimarketing.vn | admin123 | admin |
| trannhuy8425@gmail.com | (Google OAuth) | admin |
| fggjn126@gmail.com | (Google OAuth) | viewer |

---

## 2. Dashboard Tổng quan (`/`)

**Component:** `DashboardOverview.tsx` + `DashboardOverview.css`

### UI Elements
- **Live Banners:** GSC connection status (🟢 Live / 🟡 Chưa kết nối), GA4 status
- **6 Stat Cards:** Phiên truy cập, Người dùng, Lượt xem, Lượt nhấp GSC, Tỷ lệ thoát, Tương tác
- **Charts Row 1:** Bar chart "Top từ khóa theo hiển thị" + Pie chart "Phân bố vị trí"
- **Charts Row 2:** Area chart "Phiên & Lượt xem 30 ngày" + Pie chart "Nguồn lưu lượng"
- **Charts Row 3:** Table "Trang hàng đầu GA4" + Radar chart "Hiệu suất tổng quan"
- **SERP Quick Overview:** Top 5 kết quả Google cho keyword mặc định
- **Quick Actions:** 6 nút điều hướng nhanh
- **Lịch sử phân tích:** Danh sách các lần audit/phân tích gần đây

### API
- `POST /api/ai-keywords` → lấy GSC keywords cho charts
- `POST /api/ga4-overview` → lấy GA4 data (sessions, traffic sources, top pages)
- `POST /api/serp/live` → SERP overview cho keyword mặc định
- `GET /auth/google/setup` → 1-click OAuth setup

### Trạng thái
- ✅ UI hoàn chỉnh, dark glassmorphism theme
- ✅ Charts: recharts (Bar, Pie, Area, Radar)
- ⚠️ Cần GSC/GA4 credentials để có dữ liệu thật
- ⚠️ Không có credentials → hiển thị empty state + nút "Kết nối Google"

---

## 3. Trung tâm SEO → Kiểm tra SEO (`/seo-audit`)

**Component:** `SeoWorkspace.tsx` → tab "Kiểm tra SEO"

### UI Elements
- Form: URL + Từ khóa mục tiêu → nút "Phân tích SEO"
- Kết quả: Điểm SEO tổng (0-100), phân tích chi tiết theo tiêu chí
- Các tiêu chí: Title tag, Meta description, Headings, Content, Images, Links, Speed, Mobile

### API
- `POST /api/audit-url` → `{ url, keyword }` → `AuditResponse` (điểm + chi tiết)

### Trạng thái
- ✅ Hoạt động đầy đủ
- ✅ Không cần credentials bên ngoài (trực tiếp crawl URL)
- ✅ Sử dụng Groq AI để phân tích

---

## 4. Trung tâm SEO → SEO Kỹ thuật (`/technical-seo`)

**Component:** `SeoWorkspace.tsx` → tab "SEO kỹ thuật"

### UI Elements
- Form: URL → nút "Kiểm tra kỹ thuật"
- Kết quả: 8 tiêu chí kỹ thuật (robots.txt, sitemap, HTTPS, speed, mobile, structured data, canonical, meta robots)

### API
- `POST /api/technical-seo` → `{ url }` → kết quả 8 tiêu chí

### Trạng thái
- ✅ Hoạt động
- ✅ Không cần credentials

---

## 5. Trung tâm SEO → CRO & Uy tín (`/cro`)

**Component:** `SeoWorkspace.tsx` → tab "CRO & Uy tín" → `CroAuditPanel` wrapper → `CroDashboard`

### UI Elements
- Form: URL + Từ khóa → nút "Phân tích CRO"
- Kết quả: Trust signals, conversion elements, UX analysis, competitor comparison
- Dashboard: Biểu đồ radar trust score, danh sách recommendations

### API
- `POST /api/audit-url` → dùng chung audit endpoint, trích xuất `cro_analysis`

### Trạng thái
- ✅ Self-contained panel (refactored)
- ⚠️ Cần Groq API key

---

## 6. Trung tâm Từ khóa → Theo dõi Keyword (`/rank-tracker`)

**Component:** `KeywordHub.tsx` → tab "Theo dõi keyword" → `RankTracker`

### UI Elements
- Danh sách keywords đang theo dõi
- Biểu đồ ranking history (recharts LineChart)
- Nút thêm/xóa keyword
- CSV import/export
- Bảng: Keyword, Position, Change, Clicks, Impressions

### API
- `GET /api/rank-tracker/keywords` → danh sách tracked keywords
- `POST /api/rank-tracker/add` → thêm keyword
- `GET /api/rank-tracker/history/{keyword}` → lịch sử ranking
- `POST /api/rank-tracker/check` → kiểm tra ranking hiện tại

### Database
- `rank_tracker.db` → tables: `tracked_keywords`, `ranking_history`

### Trạng thái
- ✅ CRUD đầy đủ
- ✅ Chart ranking history
- ✅ CSV export
- ⚠️ Auto-check cần GSC credentials

---

## 7. Trung tâm Từ khóa → AI Keywords (`/keywords`)

**Component:** `KeywordHub.tsx` → tab "AI Keywords" → `AIKeywordsPanel`

### UI Elements (MỚI - vừa refactor)
- Form: "Từ khóa mục tiêu (tùy chọn)" → nút "Phân tích từ khóa"
- **4 Stat Cards:** Số từ khóa, Lượt nhấp, Hiển thị, Nguồn dữ liệu
- **Tóm tắt AI:** Summary text + AI provider badge
- **Bảng GSC Keywords:** #, Từ khóa, Vị trí (color-coded), Clicks, Impressions, CTR
- **Quick Wins:** Cards với keyword + position + action
- **Từ khóa đề xuất:** Cards với search intent, difficulty, priority tags
- **Nhóm chủ đề:** Cluster cards với related keywords
- **Chiến lược nội dung:** Content strategy cards

### API
- `POST /api/ai-keywords` → `{ target_keyword?: string }` → `AIKeywordsResponse`

### Response shape
```json
{
  "gsc_keywords": [{ "keyword", "clicks", "impressions", "ctr", "position" }],
  "total_clicks": 0,
  "total_impressions": 0,
  "ai_analysis": "",
  "summary": "",
  "recommended_keywords": [{ "keyword", "search_intent", "difficulty", "priority", "reason" }],
  "quick_wins": [{ "keyword", "current_position", "action" }],
  "keyword_clusters": [{ "cluster_name", "keywords", "suggested_content" }],
  "content_strategy": [{ "title", "target_keyword", "content_type", "priority", "description" }],
  "data_source": "live_gsc | no_data",
  "ai_provider": "ai | builtin | none"
}
```

### Trạng thái
- ✅ Contract đúng (vừa fix)
- ⚠️ Cần GSC credentials + Groq API key
- ⚠️ Không có GSC → hiển thị error state rõ ràng

---

## 8. Trung tâm Từ khóa → SERP trực tiếp (`/serp`)

**Component:** `KeywordHub.tsx` → tab "SERP trực tiếp" → `SerpSearchPanel` → `SerpResultsPanel`

### UI Elements
- Form: Từ khóa + Quốc gia (VN/US/UK/AU) → nút "Tra cứu SERP"
- Kết quả: Top 10 organic results (title, URL, snippet, position)
- SERP features detected
- Featured snippets, People Also Ask

### API
- `POST /api/serp/live` → `{ keyword, location, num_results }` → organic results + features

### Trạng thái
- ✅ Hoạt động
- ⚠️ Cần DataForSEO credentials

---

## 9. Trung tâm Từ khóa → Phân tích đối thủ (`/competitor`)

**Component:** `KeywordHub.tsx` → tab "Phân tích đối thủ" → `CompetitorGapPanel` → `CompetitorRadarPanel`

### UI Elements
- Form: URL của bạn + URL đối thủ 1 + URL đối thủ 2 → nút "Phân tích gap"
- Kết quả: Radar chart so sánh, bảng keyword gaps, content gaps

### API
- `POST /api/competitor-gap` → `{ your_url, competitor_urls }` → gap analysis

### Trạng thái
- ✅ Self-contained panel
- ⚠️ Cần Groq API key

---

## 10. Trung tâm Từ khóa → Chiến dịch (`/campaign`)

**Component:** `KeywordHub.tsx` → tab "Chiến dịch" → `CampaignSearchPanel` → `CampaignTrackerPanel`

### UI Elements
- Form: URL + Từ khóa → nút "Tìm cơ hội"
- Kết quả: Opportunities list, priority actions

### API
- `POST /api/opportunities` → `{ url, keyword }` → opportunities

### Trạng thái
- ✅ Self-contained panel
- ⚠️ Cần Groq API key + URL phải truy cập được

---

## 11. Xưởng Nội dung AI → Lập kế hoạch & Viết bài (`/content-planner`)

**Component:** `ContentStudio.tsx` → tab "Lập kế hoạch & Viết bài" → `ContentPlannerWrapper` → `ContentPlannerPanel`

### UI Elements
- **Phase 1 - Plan:** Form (Từ khóa chính + Đối tượng đọc + Gaps) → AI tạo kế hoạch
- **Phase 2 - Write:** Nút "Tạo outline" hoặc "Viết bài đầy đủ" (Groq AI)
- **Phase 3 - Polish:** `PolishPanel` — humanize content, chỉnh tone
- **Phase 4 - Publish:** `PublishModal` — điền WordPress URL + credentials → publish

### API Flow
1. `POST /api/plan-content` → `{ primary_keyword, target_audience, competitor_gaps }` → plan
2. `POST /api/content/write-full` → AI viết bài đầy đủ
3. `POST /api/polish/scrub` → humanize nội dung
4. `POST /api/publish` → publish to WordPress

### Trạng thái
- ✅ End-to-end flow (Plan → Write → Polish → Publish)
- ✅ Publish flow đã được nối (vừa fix)
- ⚠️ Cần Groq API key cho AI writing
- ⚠️ Cần WordPress credentials cho publish

---

## 12. Xưởng Nội dung AI → Spin & Viết lại (`/spin-editor`)

**Component:** `ContentStudio.tsx` → tab "Spin & Viết lại" → `SpinEditor`

### UI Elements
- Textarea nhập nội dung gốc
- Các tùy chọn: Tone, mức độ thay đổi
- Nút "Spin" → output viết lại

### API
- `POST /api/polish/scrub` → `{ content, mode }` → rewritten content

### Trạng thái
- ✅ Hoạt động
- ⚠️ Cần Groq API key

---

## 13. Schema & GEO Optimizer (`/geo-optimizer`)

**Component:** `GeoOptimizer.tsx`

### UI Elements
- 12 loại Schema.org generator
- Form input cho từng loại (FAQ, Product, Article, Local Business, etc.)
- Output: JSON-LD code có thể copy

### API (12 endpoints)
- `POST /api/geo/generate-faq`
- `POST /api/geo/generate-schema`
- `POST /api/geo/generate-product-schema`
- `POST /api/geo/generate-article-schema`
- ... (12 total)

### Trạng thái
- ✅ Hoạt động đầy đủ
- ✅ Không cần credentials

---

## 14. Core Web Vitals (`/core-web-vitals`)

**Component:** `CoreWebVitals.tsx`

### UI Elements
- Form: URL → nút "Kiểm tra"
- Kết quả: LCP, FID, CLS, TTFB scores
- Biểu đồ gauge cho từng metric
- Recommendations

### API
- `POST /api/seo-tools/core-web-vitals` → `{ url }` → CWV scores

### Trạng thái
- ✅ Hoạt động
- ⚠️ Cần PAGESPEED_API_KEY

---

## 15. Broken Link Checker (`/broken-links`)

**Component:** `BrokenLinkChecker.tsx`

### UI Elements
- Form: URL → nút "Quét link"
- Bảng: URL, Status code, Type (internal/external), Page source

### API
- `POST /api/seo-tools/broken-links` → `{ url }` → list of broken links

### Trạng thái
- ✅ Hoạt động
- ✅ Không cần credentials

---

## 16. Quản lý Sites (`/sites`)

**Component:** `SiteManager.tsx`

### UI Elements
- Danh sách sites đang quản lý
- Nút thêm/sửa/xóa site
- Mỗi site: Name, URL, Niche, Status, Last scan score

### Database
- `sites.db` → table: `managed_sites`

### Trạng thái
- ✅ CRUD đầy đủ

---

## 17. Quản lý Users — Admin (`/admin/users`)

**Component:** `UserManagement.tsx`

### UI Elements
- Bảng users: Email, Tên, Role, Trạng thái, Ngày tạo, Last login
- Dropdown đổi role (admin/editor/viewer)
- Nút xóa user
- Chỉ hiển thị cho role=admin

### API
- `GET /api/auth/users` → danh sách users (admin only)
- `PUT /api/auth/users/{id}/role` → đổi role
- `DELETE /api/auth/users/{id}` → xóa user

### Database
- `auth.db` → table: `users`

### Trạng thái
- ✅ Hoạt động
- ✅ ViewerGuard chặn viewer truy cập

---

## Tổng kết phụ thuộc Credentials

| Credential | Chức năng phụ thuộc |
|-----------|-------------------|
| **GROQ_API_KEY** | AI Keywords, SEO Audit, CRO, Competitor, Campaign, Content Write, Polish |
| **GSC OAuth** | Dashboard charts, AI Keywords (GSC data), Rank Tracker auto-check |
| **GA4 credentials** | Dashboard GA4 charts, sessions, traffic sources |
| **PAGESPEED_API_KEY** | Core Web Vitals |
| **DATAFORSEO** | SERP trực tiếp |
| **WordPress credentials** | Publish to WordPress |

## Chức năng KHÔNG cần credentials (hoạt động ngay)
- ✅ Đăng nhập/Đăng ký (email)
- ✅ Schema & GEO Optimizer (12 loại)
- ✅ Broken Link Checker
- ✅ Quản lý Sites
- ✅ Quản lý Users
- ✅ Technical SEO (cơ bản)
- ✅ Spin Editor (UI ready, cần Groq cho AI)
