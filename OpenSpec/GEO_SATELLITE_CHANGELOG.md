# GEO Satellite & SpinEditor Integration — Changelog

> **Ngày thực hiện:** 12/05/2026  
> **Dự án:** AI Marketing Hub  
> **Mục tiêu:** Xây dựng GEO Satellite Pipeline + Tích hợp SpinEditor methodology

---

## 🛰️ Module 1: GEO Satellite Sites

### Mô tả
Hệ thống quản lý mạng lưới blog vệ tinh (Blogger/WordPress), tự động spin nội dung bằng AI, chèn backlink, và đăng bài hàng loạt lên satellite sites.

### Workflow
```
Bài gốc → AI Spin (Groq LLaMA) → N bản unique (>70%)
                                        ↓
                              Tự động chèn backlink
                           (anchor text đa dạng, tự nhiên)
                                        ↓
                              Đăng lên Blogger/WordPress
                                        ↓
                              Track: status, index, backlink
```

### Files đã tạo/sửa

| File | Loại | Mô tả |
|------|------|-------|
| `backend/core/satellite_manager.py` | **MỚI** | Core module: CRUD sites, Blogger API v3, WordPress REST API, backlink injection, index check |
| `backend/routers/api_satellite.py` | **MỚI** | API Router: 6 endpoints cho satellite operations |
| `backend/core/spin_editor.py` | **SỬA** | Thêm `spin_for_satellite()` — tạo multi-version HTML với backlink |
| `backend/main.py` | **SỬA** | Register `api_satellite` router |
| `frontend/src/components/SatelliteManager.tsx` | **MỚI** | Component 3 tabs: Sites, Spin & Post, History |
| `frontend/src/components/SatelliteManager.css` | **MỚI** | CSS glassmorphism matching app theme |
| `frontend/src/App.tsx` | **SỬA** | Thêm 🛰️ Satellite Sites vào sidebar + routing |

### API Endpoints

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| `GET` | `/api/satellite/sites` | Danh sách satellite sites |
| `POST` | `/api/satellite/sites` | Thêm site mới (Blogger/WordPress) |
| `DELETE` | `/api/satellite/sites/{id}` | Xóa site |
| `POST` | `/api/satellite/spin-and-post` | Spin AI + đăng lên satellites |
| `POST` | `/api/satellite/post-direct` | Đăng bài trực tiếp (không spin) |
| `GET` | `/api/satellite/posts` | Lịch sử bài đã đăng |
| `POST` | `/api/satellite/check-index` | Kiểm tra Google index |

### Tính năng chi tiết

- **Quản lý Sites**: Thêm/xóa blog vệ tinh (hỗ trợ Blogger + WordPress)
- **Spin & Post**: AI spin nội dung gốc → tạo N bản unique → đăng tự động
- **Backlink Injection**: Tự chèn backlink với anchor text đa dạng (8 template)
- **Lịch sử**: Theo dõi bài đã đăng, trạng thái, index status
- **Authentication**: Sử dụng OAuth2 hiện có (chung với GSC/GA4) cho Blogger API

---

## ⭐ Module 2: Gợi Ý Từ Khóa (SpinEditor-style)

### Mô tả
Replicate tính năng "Gợi ý từ khóa" của SpinEditor — nhập seed keyword → lấy gợi ý từ Google Suggest + kiểm tra Allintitle, KQ tìm kiếm, KEI, Độ cạnh tranh.

### So sánh với SpinEditor

| Tính năng | SpinEditor | AI Marketing Hub |
|-----------|------------|------------------|
| Google Suggest | ✅ | ✅ Cùng endpoint |
| Search Volume | ✅ Database riêng (Google Ads) | ⚠️ Ước tính từ total_results |
| Allintitle | ✅ Qua browser extension | ✅ SerpAPI / Google CSE |
| KQ tìm kiếm | ✅ | ✅ SerpAPI / Google CSE |
| KEI | ✅ Volume²/Allintitle | ✅ Cùng công thức |
| Độ cạnh tranh | ✅ Low/Medium/High | ✅ Cùng phân loại |
| Check KEI hàng loạt | ✅ Extension | ✅ API tự động |

### Hạn chế so với SpinEditor

1. **Search Volume**: SpinEditor lấy từ Google Ads Keyword Planner (trả phí), chúng ta ước tính từ total_results (không chính xác bằng)
2. **Từ khóa gợi ý**: Google Suggest trả kết quả khác tuỳ IP/location — có thể khác SpinEditor
3. **API Quota**: SerpAPI giới hạn 100/tháng, CSE 100/ngày — chỉ check metrics cho top 5-10 keywords

### Files đã tạo/sửa

| File | Loại | Mô tả |
|------|------|-------|
| `backend/core/keyword_suggest.py` | **MỚI** | Module gợi ý từ khóa: Google Suggest + SerpAPI/CSE + KEI |
| `backend/routers/api_phase2.py` | **SỬA** | Thêm endpoint `POST /api/keyword-suggest` |
| `frontend/src/App.tsx` | **SỬA** | Thêm sub-tab "⭐ Gợi ý từ khóa (SpinEditor)" trong AI Keyword Analysis |

### API Endpoint

| Method | Endpoint | Body | Mô tả |
|--------|----------|------|-------|
| `POST` | `/api/keyword-suggest` | `{"keyword": "xe", "check_metrics": true, "max_keywords": 30}` | Gợi ý từ khóa + metrics |

### Pipeline xử lý

```
Seed Keyword
    ↓
Google Suggest (autocomplete)
    ↓ (mở rộng a-z suffix)
30+ keyword ideas
    ↓
SerpAPI / Google CSE (top 5-10 keywords)
    ↓
Allintitle + Total Results
    ↓
Volume Estimation (bracket mapping)
    ↓
KEI = Volume² / Allintitle
    ↓
Competition: Low / Medium / High / Very High
```

---

## 🔍 Khám phá SpinEditor

### Các trang đã trải nghiệm

| Trang | URL | Mô tả |
|-------|-----|-------|
| Gợi ý từ khóa | `/goi-y-tu-khoa` | Suggest keywords + volume, KEI, cạnh tranh |
| Viết bài | `/bai-viet-hoan-thanh` | Viết bài AI tự động, 5 loại bài |
| Đăng lên Blogger | `/post-blog` | Auto-post Blogger có hẹn giờ, nhãn |
| Đăng lên blog | `/tu-dong-dang-bai` | Auto-post WordPress + Blogger |
| Đăng lên forum | `/quan-ly-dien-dan` | Đăng diễn đàn hàng loạt |
| Thứ hạng từ khóa | `/kiem-tra-thu-hang-tu-khoa` | Track vị trí keyword |
| Tăng traffic | `/cong-dong-view` | Hệ thống cộng đồng tăng view |
| Kiểm tra tên miền | `/kiem-tra-ten-mien` | Check domain index + IP |
| KT sao chép nội dung | — | Kiểm tra trùng lặp nội dung |

### Kết luận kỹ thuật

- **Không có public API** — SpinEditor hoạt động hoàn toàn qua web + browser extension
- **ASP.NET backend** — Form POST truyền thống, session cookies
- **Google Autocomplete** — SpinEditor dùng cùng endpoint Google Suggest
- **Allintitle** — Dùng browser extension để bypass CORS, check trực tiếp Google
- **Volume** — Database riêng, có thể từ Google Ads Keyword Planner API

---

## ✅ Verification

| Kiểm tra | Kết quả |
|----------|---------|
| TypeScript `npx tsc --noEmit` | ✅ 0 errors |
| Python `py_compile` | ✅ 0 errors |
| Backend syntax | ✅ All modules compile |
| Frontend rendering | ✅ Sub-tabs hiển thị đúng |

---

## 📋 Hướng dẫn sử dụng

### Satellite Sites
1. Sidebar → **🛰️ Satellite Sites**
2. Tab **Sites** → **➕ Thêm site** → Chọn Blogger → Nhập Blog ID
3. Tab **Spin & Post** → Dán bài gốc → Chọn level/tone → **🚀 Spin & Đăng ngay**
4. Tab **Lịch sử** → Xem trạng thái đăng, backlink, index

### Gợi ý từ khóa
1. Sidebar → **AI Keyword Analysis**
2. Tab **⭐ Gợi ý từ khóa (SpinEditor)**
3. Nhập keyword (ví dụ: "xe mitsubishi") → **Gợi ý từ khóa**
4. Xem bảng kết quả: Từ khóa, Volume, Allintitle, KQ, KEI, Cạnh tranh

### Lưu ý
- **Restart backend** sau khi update code: `Ctrl+C` → `python main.py`
- **SerpAPI quota**: 100 requests/tháng — hệ thống chỉ check top 5 keywords mỗi lần
- **CSE quota**: 100 requests/ngày — fallback nếu SerpAPI hết
- **Blog ID Blogger**: Lấy từ URL dashboard `blogger.com/blog/posts/{BLOG_ID}`

---

## 🔄 Module 3: SpinEditor Auto Scraper

### Mô tả
Tự động cào dữ liệu keyword (search volume THẬT) từ SpinEditor — không cần copy/paste thủ công.

### Files đã tạo/sửa

| File | Loại | Mô tả |
|------|------|-------|
| `backend/core/spineditor_scraper.py` | **MỚI** | Auto scraper: session mgmt, page fetch, DoAction API, HTML parser |
| `backend/routers/api_phase2.py` | **SỬA** | 3 endpoints mới: scrape, save-cookies, session-status |
| `backend/data/spineditor_session.json` | **MỚI** | Lưu cookies session SpinEditor |
| `frontend/src/App.tsx` | **SỬA** | Nút "🔄 Cào từ SpinEditor" + handler |

### API Endpoints

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| `POST` | `/api/spineditor/scrape` | Cào keyword data từ SpinEditor |
| `POST` | `/api/spineditor/save-cookies` | Lưu/cập nhật cookies |
| `GET` | `/api/spineditor/session-status` | Kiểm tra trạng thái session |

### Lưu ý
- **Cookies hết hạn**: SpinEditor session sẽ hết hạn (1-7 ngày). Cần cập nhật lại.
- **Dữ liệu thật**: Search volume từ Google Keyword Planner — chính xác hơn ước tính.

---

## 📊 Module 4: Lịch Sử Sử Dụng (Usage History)

### Mô tả
Middleware tự động ghi lại toàn bộ API calls — input, output, status, thời gian xử lý. Giúp debug và monitor hệ thống.

### Files đã tạo/sửa

| File | Loại | Mô tả |
|------|------|-------|
| `backend/core/usage_history.py` | **MỚI** | Logger: log_usage, get_history, get_stats, clear |
| `backend/main.py` | **SỬA** | UsageHistoryMiddleware + 3 API endpoints |
| `frontend/src/components/UsageHistory.tsx` | **MỚI** | UI: stats cards + log table + detail modal + endpoint stats |
| `frontend/src/App.tsx` | **SỬA** | Thêm tab "📊 Lịch sử dụng" trong Quản lý |
| `backend/data/usage_history.json` | **TỰ ĐỘNG** | File lưu log (tự tạo khi có API call) |

### Tính năng
- **Auto-logging**: Mọi `/api/*` call tự động ghi lại (không cần code thêm)
- **Stats Cards**: Tổng calls, thành công, lỗi, tỷ lệ thành công
- **Detail Modal**: Click vào row → xem Input/Output JSON chi tiết
- **Endpoint Stats**: Bảng thống kê theo từng endpoint
- **Filter**: Lọc theo endpoint
- **Clear**: Xóa toàn bộ lịch sử

### API Endpoints

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| `GET` | `/api/usage-history?limit=50&endpoint=...` | Lấy lịch sử (mới nhất trước) |
| `GET` | `/api/usage-stats` | Thống kê tổng hợp |
| `DELETE` | `/api/usage-history` | Xóa lịch sử |
