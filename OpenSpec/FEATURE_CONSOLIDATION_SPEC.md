# FEATURE CONSOLIDATION SPEC - AI Marketing Hub
<!-- Updated: 2026-05-23 -->

## 1. Muc tieu

Du an hien co qua nhieu route top-level va nhieu tinh nang chong lan ve UX. Muc tieu cua dot nay la gom lai thong tin, giam do on cua san pham, va to chuc lai giao dien theo luong cong viec cua nguoi dung thay vi theo tung engine noi bo.

Ket qua mong muon:
- Giam so khu vuc dieu huong chinh xuong 6-7 nhom ro rang
- Gop cac tinh nang trung ngu canh vao cung mot workspace
- Giu nguyen logic backend hien tai trong giai doan 1
- Khong xoa tinh nang dang hoat dong, uu tien doi cho dung cho no
- Don App.tsx de de maintain va de demo

## 2. Van de hien tai

### 2.1 Menu dang bi phan manh
Nhieu route dang la top-level nhung thuc chat chi la cong cu con:
- /seo-audit
- /technical-seo
- /cro
- /serp
- /backlinks
- /core-web-vitals
- /broken-links
- /schema-validator
- /keywords
- /competitor
- /campaign
- /content-planner
- /spin-editor
- /geo-optimizer

### 2.2 Nhieu tinh nang trung luong su dung
- SEO Audit, Technical SEO, CRO, Core Web Vitals, Broken Links, Schema Validator, Backlinks deu la cac buoc phan tich mot website/url.
- AI Keywords, Competitor, SERP, Campaign, Rank Tracker deu thuoc nhom research va keyword intelligence.
- Content Planner, AI Writer, Polish/Humanize, Spin Editor, Publish deu thuoc mot chu trinh tao noi dung.
- Geo Optimizer va Schema Validator dang chong lan ro rang.

### 2.3 Cau truc frontend va backend kho maintain
- frontend/src/App.tsx dang qua lon va om qua nhieu page logic.
- backend routers dang chia theo phase thay vi chia theo domain nghiep vu.

## 3. Muc tieu IA moi

San pham sau khi gom tinh nang se co 7 khu vuc chinh:

1. Tong quan
2. SEO Workspace
3. Keyword Intelligence
4. AI Content Studio
5. Schema & GEO
6. Operations
7. Cai dat

## 4. Mapping route cu -> nhom moi

### 4.1 Tong quan
- / -> DashboardOverview

### 4.2 SEO Workspace
Gop cac route sau vao cung mot workspace, dung tabs hoac section ben trong mot man hinh:
- /seo-audit
- /technical-seo
- /cro
- /backlinks
- /core-web-vitals
- /broken-links
- /schema-validator

Yeu cau UX:
- Mot form nhap URL chinh
- Mot header chung mo ta tong quan SEO
- Moi cong cu la 1 tab hoac panel
- Co kha nang giu input khi chuyen tab

### 4.3 Keyword Intelligence
Gop cac route sau:
- /keywords
- /competitor
- /serp
- /campaign
- /rank-tracker

Yeu cau UX:
- Chia thanh 3 cum: Nghien cuu, Doi thu, Theo doi
- Rank Tracker co the la tab rieng vi du lon
- Campaign khong con la top-level item, dua thanh mot phan cua co hoi tu khoa

### 4.4 AI Content Studio
Gop cac route va luong sau:
- /content-planner
- /spin-editor
- AI article writing trong Content Planner
- Polish/Humanize panel
- Publish modal

Yeu cau UX:
- Day la 1 workflow lien tuc: plan -> write -> polish -> spin neu can -> publish
- Spin Editor khong con la module top-level
- Neu can, tach thanh cac buoc hoac tabs trong cung mot page

### 4.5 Schema & GEO
Gop:
- /geo-optimizer
- /schema-validator

Yeu cau UX:
- 3 tab ro rang: Phan tich, Tao schema, Kiem tra schema
- Khong de user phai doan su khac nhau giua GEO va schema tools

### 4.6 Operations
Gom cac tinh nang van hanh va phu tro:
- /content-calendar
- /ab-testing
- /report
- /file-converter

Yeu cau UX:
- Khong de cac tool nay tranh do uu tien voi khu vuc core
- Co the dua vao nhom phu trong sidebar

### 4.7 Cai dat
Gom:
- /sites
- /google-setup
- /admin/users
- Satellite manager neu tiep tuc su dung

Yeu cau UX:
- Doi ten Google Setup thanh "Cau hinh he thong" hoac "Ket noi & API"
- Nhom nay uu tien admin/owner, khong can dat qua noi bat trong san pham

## 5. Tinh nang nen ha cap hoac an tam thoi

Nhung tinh nang sau khong nen de top-level trong giai doan tiep theo:
- Spin Editor
- Campaign
- Schema Validator
- Core Web Vitals
- Broken Links
- Backlinks
- CRO

Nhung tinh nang sau can xac nhan truoc khi dua ra menu:
- Usage History
- Satellite Manager

Neu chua co vai tro ro rang trong demo chinh, an khoi menu.

## 6. Nguyen tac trien khai

- Khong dung Tailwind
- UI text phai la tieng Viet
- Khong doi logic backend neu chua can
- Uu tien refactor UI navigation va page composition truoc
- Giai doan 1 khong bat buoc doi endpoint
- Neu can tao page moi, uu tien page container moi thay vi viet them logic vao App.tsx
- Bao toan route cu neu can cho backward compatibility, nhung sidebar va UX moi phai dua user vao cau truc moi

## 7. Ke hoach ky thuat de Claude thuc hien

### Phase 1 - Chot IA moi va shell moi
- Refactor sidebar theo 7 nhom chinh
- Refactor topbar/page header de phan cap thong tin ro hon
- Giam so item top-level hien thi

### Phase 2 - Gop workspace lon
- Tao page hoac container cho SEO Workspace
- Tao page hoac container cho Keyword Intelligence
- Tao page hoac container cho AI Content Studio
- Tao page hoac container cho Schema & GEO

### Phase 3 - Don code
- Tach bot logic khoi App.tsx
- Chuyen inline page thanh component/page rieng
- Chuan hoa title, description, nav metadata

### Phase 4 - Kiem tra lai
- TypeScript pass
- Build production pass
- Route chinh render on dinh
- Khong vo luong dang nhap
- Khong mat feature dang co

## 8. Tieu chi hoan thanh

Dot nay duoc xem la dat khi:
- User nhin menu khong con cam giac qua tai
- Moi nhom tinh nang co ten goi de hieu theo cong viec
- Cac cong cu cung ngu canh duoc dat chung trong mot workspace
- App.tsx gon hon va de bao tri hon
- Demo flow ngan gon hon, logic hon

## 9. Verification bat buoc

Frontend:
- npx tsc -p tsconfig.app.json --noEmit
- npm run build

Neu co the, smoke test cac route:
- /login
- /
- /seo-audit hoac route workspace SEO moi
- /content-planner hoac route AI Content Studio moi
- /rank-tracker hoac route Keyword Intelligence moi

## 10. Out of scope cho dot nay

- Viet lai backend hoan toan theo domain
- Xoa hinh nang co du lieu dang su dung thuc te
- PostgreSQL migration
- Mobile app
- Rebrand toan bo du an
