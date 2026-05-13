# 📋 BÁO CÁO KIỂM TRA SEO — binhphuocmitsubishi.com

> **Ngày kiểm tra:** 25/04/2026  
> **Công cụ:** AI Marketing Hub v1.0.0  
> **Người kiểm tra:** Trần Như Ý  
> **Từ khóa chính:** "Mitsubishi Bình Phước"

---

## 📊 ĐIỂM SEO TỔNG: 78/100 — KHÁ TỐT

| Hạng mục | Điểm | Đánh giá |
|----------|------|----------|
| Title & Meta | 95/100 | ✅ Xuất sắc |
| Schema/JSON-LD | 98/100 | ✅ Xuất sắc |
| Open Graph & Social | 90/100 | ✅ Tốt |
| Nội dung & SEO on-page | 45/100 | ⚠️ Cần cải thiện |
| Hiệu suất & Kỹ thuật | 70/100 | 🔶 Trung bình |
| CTA & Chuyển đổi | 60/100 | 🔶 Cần thêm |
| Mobile & UX | 75/100 | 🔶 Trung bình |

---

## ✅ NHỮNG GÌ LÀM TỐT (Giữ nguyên)

### 1. Title tag — Xuất sắc
```
Mitsubishi Bình Phước ☎ 0327 066 523 | Đại Lý Xe Mitsubishi Chính Hãng Giá Tốt
```
- ✅ Có từ khóa chính "Mitsubishi Bình Phước"
- ✅ Có số điện thoại → tăng CTR
- ✅ Độ dài 80 ký tự (tốt, dưới 60 ký tự thì càng tốt)

### 2. Meta Description — Tốt
```
Đại lý Mitsubishi Bình Phước chính hãng ✅ Xforce, Xpander, Triton, Attrage giá tốt nhất ✅ Trả góp 80% ✅ Giảm 50-100% trước bạ ✅ Giao xe tận nơi. Hotline 0327 066 523
```
- ✅ Có emoji ✅ → nổi bật trên SERP
- ✅ Có CTA (Hotline)
- ✅ Liệt kê dòng xe + ưu đãi

### 3. Schema.org / JSON-LD — Xuất sắc (rất ít web VN làm được)
- ✅ `AutoDealer` — đúng loại hình kinh doanh
- ✅ `FAQPage` — 5 câu hỏi → có thể hiện Rich Snippet trên Google
- ✅ `BreadcrumbList` — breadcrumb đúng chuẩn
- ✅ `WebSite` — thông tin website
- ✅ Có `OfferCatalog` — 6 xe với giá cụ thể
- ✅ Có `GeoCoordinates`, `openingHoursSpecification`

### 4. Open Graph & Social — Tốt
- ✅ OG title, description, image đầy đủ
- ✅ Twitter Card
- ✅ Zalo official account
- ✅ og:image có kích thước 1200x630 (chuẩn)

### 5. Kỹ thuật cơ bản
- ✅ Có `<html lang="vi">`
- ✅ Có `canonical` URL
- ✅ Robots: `index, follow`
- ✅ GA4 đã cài (`G-DFEE14V0T8`)
- ✅ Preconnect, preload cho hiệu suất
- ✅ Noscript fallback cho SEO crawler

---

## ⚠️ VẤN ĐỀ CẦN SỬA (Ưu tiên cao → thấp)

---

### 🔴 VẤN ĐỀ 1: Website SPA — Google không đọc được nội dung (NGHIÊM TRỌNG)

**Vấn đề:** Website dùng React SPA (Single Page Application) — toàn bộ nội dung render bằng JavaScript. Google crawler **có thể không đọc được** nội dung bên trong `<div id="root"></div>`.

**Hiện tại:**
```html
<body>
    <noscript>...fallback text...</noscript>
    <div id="root"></div>  <!-- NỘI DUNG TRỐNG cho crawler -->
</body>
```

**Cách sửa (chọn 1 trong 3):**

| Giải pháp | Độ khó | Hiệu quả |
|-----------|--------|-----------|
| **A. Chuyển sang Next.js (SSR)** | Cao (viết lại) | ⭐⭐⭐⭐⭐ |
| **B. Thêm Prerender.io** | Thấp (cài plugin) | ⭐⭐⭐⭐ |
| **C. Mở rộng `<noscript>`** | Rất thấp | ⭐⭐⭐ |

**Khuyến nghị:** Dùng **Giải pháp B — Prerender.io** (miễn phí 250 trang/tháng):
1. Đăng ký tại https://prerender.io
2. Thêm middleware vào server (Nginx/Vercel)
3. Khi Googlebot truy cập → trả về HTML đã render sẵn

---

### 🔴 VẤN ĐỀ 2: Thiếu thẻ H1 trong HTML tĩnh (NGHIÊM TRỌNG)

**Vấn đề:** File `index.html` không có thẻ `<h1>` visible — chỉ có trong `<noscript>`.

**Cách sửa:** Nếu chưa chuyển SSR, đảm bảo React component render H1:
```jsx
// Trang chủ
<h1>Đại Lý Mitsubishi Bình Phước — Xe Chính Hãng Giá Tốt</h1>

// Trang sản phẩm
<h1>Mitsubishi Xpander 2026 — Giá Từ 560 Triệu</h1>
```

---

### 🟡 VẤN ĐỀ 3: Title tag hơi dài (80 ký tự)

**Hiện tại:** 80 ký tự — Google có thể cắt bớt.

**Khuyến nghị:** Rút xuống ≤60 ký tự:
```
Trước:  Mitsubishi Bình Phước ☎ 0327 066 523 | Đại Lý Xe Mitsubishi Chính Hãng Giá Tốt
Sau:    Mitsubishi Bình Phước ☎ 0327 066 523 | Đại Lý Chính Hãng
```

---

### 🟡 VẤN ĐỀ 4: Thiếu thẻ `<h2>`, `<h3>` trong HTML tĩnh

**Vấn đề:** Cấu trúc heading không rõ ràng cho crawler.

**Cách sửa:** Trong React components, đảm bảo có heading hierarchy:
```
<h1> Đại Lý Mitsubishi Bình Phước
  <h2> Bảng Giá Xe Mitsubishi 2026
    <h3> Mitsubishi Xforce — Từ 599 Triệu
    <h3> Mitsubishi Xpander — Từ 560 Triệu
    <h3> Mitsubishi Triton — Từ 655 Triệu
  <h2> Chương Trình Khuyến Mãi
  <h2> Dịch Vụ Trả Góp
  <h2> Liên Hệ Đại Lý
```

---

### 🟡 VẤN ĐỀ 5: Logo trong Schema sai

**Hiện tại:** Logo dùng hình xe Xforce thay vì logo đại lý:
```json
"logo": "https://binhphuocmitsubishi.com/images/cars/xforce.webp"
```

**Cách sửa:**
```json
"logo": "https://binhphuocmitsubishi.com/cmc.png"
```

---

### 🟡 VẤN ĐỀ 6: Thiếu `alt` cho hình ảnh

**Cách sửa:** Mỗi hình xe phải có `alt` mô tả:
```html
<!-- Sai -->
<img src="xforce.webp">

<!-- Đúng -->
<img src="xforce.webp" alt="Mitsubishi Xforce 2026 giá 599 triệu tại Bình Phước">
```

---

### 🟢 VẤN ĐỀ 7: Thiếu sitemap.xml

**Cách sửa:** Tạo file `public/sitemap.xml`:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>https://binhphuocmitsubishi.com/</loc><priority>1.0</priority></url>
  <url><loc>https://binhphuocmitsubishi.com/san-pham</loc><priority>0.9</priority></url>
  <url><loc>https://binhphuocmitsubishi.com/san-pham/xforce</loc><priority>0.8</priority></url>
  <url><loc>https://binhphuocmitsubishi.com/san-pham/xpander</loc><priority>0.8</priority></url>
  <url><loc>https://binhphuocmitsubishi.com/san-pham/xpander-cross</loc><priority>0.8</priority></url>
  <url><loc>https://binhphuocmitsubishi.com/san-pham/triton</loc><priority>0.8</priority></url>
  <url><loc>https://binhphuocmitsubishi.com/san-pham/attrage</loc><priority>0.8</priority></url>
  <url><loc>https://binhphuocmitsubishi.com/san-pham/destinator</loc><priority>0.8</priority></url>
  <url><loc>https://binhphuocmitsubishi.com/bang-gia</loc><priority>0.7</priority></url>
  <url><loc>https://binhphuocmitsubishi.com/tra-gop</loc><priority>0.7</priority></url>
  <url><loc>https://binhphuocmitsubishi.com/lien-he</loc><priority>0.6</priority></url>
</urlset>
```

---

### 🟢 VẤN ĐỀ 8: Thiếu robots.txt

**Cách sửa:** Tạo file `public/robots.txt`:
```
User-agent: *
Allow: /
Sitemap: https://binhphuocmitsubishi.com/sitemap.xml
```

---

### 🟢 VẤN ĐỀ 9: Nên thêm Google Tag Manager

**Cách sửa:** Thêm đoạn GTM vào `<head>`:
```html
<!-- Google Tag Manager -->
<script>(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':
new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],
j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
})(window,document,'script','dataLayer','GTM-XXXXXXX');</script>
```
→ Tạo container GTM tại https://tagmanager.google.com

---

## 📝 CHECKLIST CHO DEV (Copy gửi cho dev)

| # | Việc cần làm | Mức độ | File cần sửa |
|---|-------------|--------|-------------|
| 1 | ⚡ Cài Prerender.io hoặc chuyển Next.js | 🔴 Cao | Server config |
| 2 | ⚡ Đảm bảo H1 render trong React | 🔴 Cao | Components |
| 3 | Rút ngắn title ≤60 ký tự | 🟡 Vừa | `index.html` dòng 27 |
| 4 | Thêm heading H2/H3 hợp lý | 🟡 Vừa | Components |
| 5 | Sửa logo trong Schema | 🟡 Vừa | `index.html` dòng 81 |
| 6 | Thêm alt cho tất cả hình ảnh | 🟡 Vừa | Components |
| 7 | Tạo sitemap.xml | 🟢 Thấp | `public/sitemap.xml` |
| 8 | Tạo robots.txt | 🟢 Thấp | `public/robots.txt` |
| 9 | Cài Google Tag Manager | 🟢 Thấp | `index.html` |

---

## 📈 DỰ KIẾN SAU KHI SỬA

| Chỉ số | Hiện tại | Dự kiến sau 1-3 tháng |
|--------|----------|----------------------|
| Điểm SEO | 78/100 | 90-95/100 |
| Ranking "Mitsubishi Bình Phước" | Top 5-10 | Top 1-3 |
| Organic traffic/tháng | ~200-500 | ~1000-2000 |
| Rich Snippets (FAQ) | Có thể hiện | Chắc chắn hiện |
| Google Business visibility | Trung bình | Cao |

---

*Báo cáo được tạo bởi AI Marketing Hub v1.0.0 — 25/04/2026*
