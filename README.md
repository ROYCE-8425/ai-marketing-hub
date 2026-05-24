# 🚀 AI Marketing Hub

**Nền tảng AI-powered SEO & Marketing automation dành riêng cho thị trường Việt Nam.**

Được thiết kế với kiến trúc hiện đại, kết hợp sức mạnh của **Groq LLaMA 3.3 70B** để tự động hóa hoàn toàn các quy trình SEO, phân tích nội dung, theo dõi thứ hạng và nghiên cứu đối thủ.

---

## 🌟 Tính năng nổi bật

*   **🕵️‍♂️ Live SERP & AI Deep Analysis**: Quét kết quả tìm kiếm Google (SERP) trực tiếp theo thời gian thực và dùng AI "mổ xẻ" kỹ thuật On-page SEO của bài viết Top 1.
*   **🤖 Content AI Engine**: Lên kế hoạch từ khóa, tự động viết bài SEO chất lượng cao và Spin Editor (tái tạo nội dung) bằng sức mạnh siêu việt của LLaMA 3.3.
*   **⚙️ Technical SEO & Audit**: Chẩn đoán trang web với Core Web Vitals, kiểm tra link hỏng (Broken Links), xác thực Schema JSON-LD.
*   **📈 Rank Tracker**: Theo dõi thứ hạng từ khóa liên tục qua dữ liệu kết hợp từ Google Search Console (GSC) và SerpAPI.
*   **🔗 Phân tích Backlink**: Phân tích hồ sơ liên kết nội bộ, liên kết ngoài, đánh giá chất lượng Dofollow/Nofollow.
*   **🌐 Quản lý Multi-site**: Quản lý nhiều website cùng lúc, báo cáo định kỳ.

## 🛠 Tech Stack

**Frontend:**
*   React 19 + TypeScript 6 + Vite 8
*   Giao diện: **Dark Glassmorphism** mượt mà (Vanilla CSS - *Không dùng Tailwind*)
*   Data Visualization: Recharts

**Backend:**
*   **FastAPI** (Python 3.12+) với kiến trúc xử lý bất đồng bộ.
*   **AI Engine**: Groq API (LLaMA 3.3 70B) với khả năng thấu hiểu tiếng Việt sâu sắc.
*   **Database**: 6 cơ sở dữ liệu SQLite riêng biệt cho từng phân hệ (Sites, Rank Tracker, Content Calendar, A/B Tests, Auth, Usage Logs).
*   **Bảo mật**: Xác thực JWT Token & Phân quyền RBAC.

**DevOps & Triển khai:**
*   Docker & Docker Compose (Multi-stage builds) tối ưu dung lượng.
*   Nginx Web Server.

## 📁 Cấu trúc thư mục dự án

```text
ai-marketing-hub/
├── frontend/             # 💻 Mã nguồn React SPA (Vite)
│   ├── src/
│   │   ├── components/   # Các UI Component (SerpResultsPanel, BacklinkAnalyzer...)
│   │   ├── hooks/        # Custom React Hooks
│   │   ├── lib/          # Utilities, Auth Config, API Config
│   │   └── index.css     # CSS cốt lõi định hình phong cách Glassmorphism
├── backend/              # ⚙️ Mã nguồn FastAPI
│   ├── routers/          # Các endpoint API (90+ endpoints)
│   ├── core/             # Logic nghiệp vụ, gọi AI, thao tác DB
│   ├── data/             # Thư mục chứa cơ sở dữ liệu SQLite
│   └── main.py           # Entry point của server FastAPI
├── OpenSpec/             # 📚 Tài liệu kỹ thuật, Context & Diagrams
└── docker-compose.yml    # Cấu hình triển khai hệ thống
```

## 🚀 Hướng dẫn cài đặt & Chạy (Local)

### 1. Backend (FastAPI)

```bash
cd backend
# Cài đặt thư viện
pip install -r requirements.txt

# Khởi tạo 6 cơ sở dữ liệu (chỉ chạy lần đầu)
python init_database.py

# Khởi động server
python -m uvicorn main:app --reload --port 8000
```
> **Lưu ý:** Bạn cần cấu hình file `.env` theo `backend/.env.example`, điền đủ `GROQ_API_KEY`, `SERPAPI_KEY` và các thiết lập GSC.

### 2. Frontend (React + Vite)

```bash
cd frontend
# Cài đặt Node modules
npm install

# Khởi động dev server
npm run dev
```
Trang web sẽ chạy tại: `http://localhost:5173`

## 🐳 Triển khai bằng Docker (Production)

Để triển khai hệ thống lên VPS Linux, bạn chỉ cần sử dụng Docker:

```bash
# Xây dựng lại container nếu có cập nhật code
docker-compose build

# Khởi động toàn bộ hệ thống ở chế độ nền
docker-compose up -d
```

## 👨‍💻 Thông tin dự án

*   **Tác giả:** Trần Như Ý
*   **Phiên bản hiện tại:** v3.2.0 (Phase 20+)
*   **Bản quyền:** Đóng (Dự án riêng)
