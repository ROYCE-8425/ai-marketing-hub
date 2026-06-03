# AI ADVISOR V2 SPEC - AI Marketing Hub
<!-- Updated: 2026-06-03 -->

## 1. Muc tieu

Nang cap `AI Advisor` tu mot man hinh tom tat dieu hanh thanh mot workspace co van thuc su, phuc vu duoc 3 nhom nhu cau:

1. Nguoi quan ly can xem nhanh website dang yeu o dau
2. Nguoi lam SEO can dao sau vao bang chung, page, keyword, issue
3. Nguoi van hanh / agency can xuat bao cao va giao viec theo lo trinh

AI Advisor v2 phai giai quyet 3 nang luc moi:

- `Deep Analysis`: phan tich sau hon, co bang chung va muc do tin cay
- `Report Export`: xuat bao cao de tai ve va chia se
- `Roadmap Tree`: tao cay lo trinh hanh dong co uu tien, phu thuoc va tac dong

Muc tieu cuoi cung:
- bien AI Advisor thanh `AI Diagnostic Workspace`
- khong chi la mot doan AI summary

## 2. Van de hien tai

AI Advisor phase 1 da co cac dau ra co gia tri:
- summary
- top_issues
- quick_wins
- technical_blockers
- content_opportunities
- action_plan_7d
- action_plan_30d
- data_snapshot
- source_status

Nhung output hien tai van con cac gioi han:

### 2.1 Chua du sau cho user nang cao

User nang cao se hoi them:
- vi sao issue nay duoc uu tien?
- bang chung cu the nam o keyword nao, page nao?
- tac dong uoc tinh len KPI la gi?
- sua xong thi kiem tra lai nhu the nao?
- viec nao la dependency cua viec nao?

Hien tai AI Advisor chua tra loi duoc ro cac cau hoi nay bang cau truc du lieu.

### 2.2 Dang hien thi theo kieu "list report"

UI hien tai chu yeu la:
- section summary
- section top issues
- section quick wins
- section action plans

No chua phan cap thanh:
- tong quan
- dao sau
- lo trinh
- bao cao

### 2.3 Chua co kha nang xuat bao cao

AI Advisor chua co workflow:
- preview report
- tai Markdown
- tai PDF
- tai DOCX

Dieu nay lam giam gia tri su dung thuc te voi:
- agency
- SEO lead
- account manager
- khach hang muon nhan bao cao

### 2.4 Chua co cau truc roadmap tree

Action plan hien tai la danh sach tuan tu.
No chua mo ta duoc:
- task nao la task goc
- task nao phu thuoc task nao
- stream nao can lam truoc
- viec nao la quick win, viec nao la strategic

## 3. Dinh huong san pham

AI Advisor v2 se duoc dinh vi la:

- `AI Diagnostic Workspace`
- `AI Report Generator`
- `AI Roadmap Planner`

No khong thay the cac tool hien co.
No dong vai tro tong hop, uu tien hoa, va chuyen du lieu thanh quyet dinh va ke hoach hanh dong.

## 4. Kien truc trai nghiem de xuat

AI Advisor v2 nen duoc chia thanh 4 tabs chinh:

### 4.1 Tong quan

Muc tieu:
- cho user thay toan canh trong 1-2 phut

Noi dung:
- executive summary
- confidence score
- source coverage
- top issues
- quick wins
- technical blockers
- top pages / top keywords can uu tien

### 4.2 Phan tich chuyen sau

Muc tieu:
- cho phep user dao sau vao tung insight

Noi dung:
- deep insights cards
- evidence panels
- affected pages
- affected keywords
- fix steps
- validation checks
- source dependency

### 4.3 Lo trinh hanh dong

Muc tieu:
- chuyen recommendation thanh workflow thuc thi

Noi dung:
- roadmap tree
- workstreams
- action plan 7 ngay
- action plan 30 ngay
- priority / impact / effort filters
- task dependency view

### 4.4 Bao cao

Muc tieu:
- cho user tai, chia se, hoac gui bao cao

Noi dung:
- report preview
- tai Markdown
- tai PDF
- tai DOCX
- copy executive summary
- export action plan

## 5. Deep Analysis model

### 5.1 Nguyen tac

Khong de AI viet mot doan phan tich mo rong tu do.
Deep analysis phai la `structured analysis`, dua tren:
- deterministic insights da co
- snapshot data
- source_status
- confidence

### 5.2 Moi deep insight nen co

Moi insight trong `deep_insights` nen chua:

- `id`
- `category`
- `severity`
- `title`
- `why_it_matters`
- `evidence`
- `affected_pages`
- `affected_keywords`
- `source_dependencies`
- `estimated_effort`
- `expected_impact`
- `confidence`
- `fix_steps`
- `validation_check`

### 5.3 Vi du deep insight

Vi du insight ve CTR:
- title: CTR thap o nhom tu khoa gan top dau
- evidence:
  - keyword A co impressions cao, vi tri 4.2, CTR 0.8%
  - keyword B co impressions cao, vi tri 5.1, CTR 1.1%
- affected_pages:
  - page dich vu chinh
  - page brand landing
- why_it_matters:
  - co nhu cau that nhung snippet chua du hap dan
- expected_impact:
  - tang CTR va organic clicks nhanh hon viec viet content moi
- validation_check:
  - do lai CTR sau 14 ngay

## 6. Roadmap Tree model

### 6.1 Muc tieu

Roadmap tree giup user nhin thay:
- muc tieu tong
- stream cong viec lon
- task con
- dependency
- uu tien
- thu tu mo khoa

### 6.2 Cau truc de xuat

Roadmap tree gom 3 tang:

#### Tang 1: Goal root
- Muc tieu tang truong cho website

#### Tang 2: Strategic workstreams
- Technical foundation
- CTR & SERP optimization
- Content expansion
- Trust / Entity / GEO

#### Tang 3: Action nodes
- task cu the
- co priority
- co impact
- co effort
- co ETA
- co dependency

### 6.3 Moi roadmap task nen co

- `id`
- `parent_id`
- `phase`
- `category`
- `task`
- `depends_on`
- `priority`
- `estimated_effort`
- `expected_impact`
- `owner_type`
- `kpi_target`
- `validation_metric`
- `status`

### 6.4 Nguyen tac sinh cay

Khong de AI tu "ve cay" khong cau truc.
Can:
- sinh tasks co structure truoc
- sau do UI render thanh tree

Roadmap tree phai duoc tao tu:
- deterministic priorities
- ai summary co kiem soat
- task metadata ro rang

## 7. Report Export model

### 7.1 Cac dinh dang can ho tro

Phase 1:
- Markdown
- HTML

Phase 2:
- PDF
- DOCX

### 7.2 Noi dung report

Bao cao nen co:

1. Tieu de / thong tin website
2. Executive summary
3. Confidence va source coverage
4. Top issues
5. Quick wins
6. Technical blockers
7. Content opportunities
8. Deep insights
9. Action plan 7 ngay
10. Action plan 30 ngay
11. Roadmap tree
12. Appendix: snapshot du lieu

### 7.3 Nguyen tac xuat bao cao

Khong de AI viet lai report tu dau moi lan.
Nen dung:
- structured report template
- AI chi viet cac block can dien giai

Nhu vay report:
- sat du lieu hon
- de defend hon
- format on dinh hon

## 8. Backend response shape moi de xuat

Ngoai cac field hien tai, AI Advisor v2 nen mo rong response voi:

### 8.1 `deep_insights`

```json
[
  {
    "id": "ctr_low_high_impression",
    "category": "ctr",
    "severity": "high",
    "title": "CTR thap o nhom tu khoa gan top dau",
    "why_it_matters": "...",
    "evidence": [],
    "affected_pages": [],
    "affected_keywords": [],
    "source_dependencies": ["gsc"],
    "estimated_effort": "medium",
    "expected_impact": "high",
    "confidence": 0.87,
    "fix_steps": [],
    "validation_check": "..."
  }
]
```

### 8.2 `roadmap_tree`

```json
{
  "goal": "Tang truong organic cho website",
  "streams": [
    {
      "id": "technical_foundation",
      "title": "Nen tang ky thuat",
      "children": []
    }
  ]
}
```

### 8.3 `report_sections`

Dung de phuc vu export report:

- `executive_summary`
- `issue_overview`
- `quick_win_summary`
- `technical_summary`
- `content_summary`
- `roadmap_summary`
- `appendix`

### 8.4 `advisor_meta`

De giai thich report va roadmap:
- version
- generated_mode
- ai_provider
- deterministic_ratio
- heuristic_ratio
- export_ready

## 9. Backend architecture de xuat

### 9.1 File co the mo rong

- `backend/core/site_advisor.py`
- `backend/routers/api_advisor.py`

### 9.2 Core modules nen them

Goi y:
- `backend/core/advisor_deep_analysis.py`
- `backend/core/advisor_roadmap_builder.py`
- `backend/core/advisor_report_builder.py`

Neu muon giu nhe phase dau, co the dat chung trong `site_advisor.py` truoc, nhung huong dai han nen tach.

### 9.3 Endpoint de xuat

Giữ endpoint hien tai:
- `POST /api/advisor/analyze`

Them endpoint moi:
- `POST /api/advisor/report`
- `GET /api/advisor/history`
- `GET /api/advisor/history/{run_id}`

Tuy chon phase sau:
- `GET /api/advisor/report/{run_id}`
- `POST /api/advisor/roadmap`

## 10. Frontend architecture de xuat

### 10.1 File chinh

- `frontend/src/components/AiAdvisor.tsx`

### 10.2 Co the tach them

- `AiAdvisorOverview.tsx`
- `AiAdvisorDeepInsights.tsx`
- `AiAdvisorRoadmap.tsx`
- `AiAdvisorReport.tsx`
- `AiAdvisorHistory.tsx`

### 10.3 Visualization de xuat

Phase 1:
- custom tree/timeline bang CSS + SVG connectors

Phase 2:
- chi can nhac neu that su can interactive graph
- co the can nhac React Flow

Khuyen nghi:
- phase 1 khong them dependency nang
- uu tien custom tree de kiem soat UI tot hon

## 11. Thu tu trien khai

### Phase 1
- mo rong response model
- them `deep_insights`
- them task metadata cho action items
- them `roadmap_tree`

### Phase 2
- refactor UI Advisor thanh 4 tabs
- them detail panels
- them roadmap tree visualization

### Phase 3
- them report preview
- xuat Markdown / HTML

### Phase 4
- xuat PDF / DOCX
- them history va compare runs

## 12. Definition of Done

AI Advisor v2 duoc coi la dat khi:

1. Co `deep_insights` co cau truc, khong chi la text summary
2. Co `roadmap_tree` hien thi duoc trong UI
3. User co the xem action plan theo dependencies va priorities
4. Co the export it nhat 1 dinh dang report tai ve duoc
5. UI khong con chi la mot trang list dai noi tiep
6. Du lieu xuat report sat voi response backend, khong fabricate

## 13. Khong duoc lam

- Khong de AI viet report tu do khong control structure
- Khong ve roadmap bang mock data
- Khong coi roadmap tree chi la hieu ung UI
- Khong tang do sau bang cach chen them nhieu van ban mo ho
- Khong export report tu data thieu ma khong ghi ro confidence va source coverage

## 14. Ghi chu quan trong

AI Advisor v2 khong thay doi triet de phase 1.
No la lop nang cap de:
- tang gia tri su dung that
- tang kha nang bao cao
- tang kha nang giao viec
- tang ban sac san pham

Neu phase 1 la "AI co van tong hop",
thi phase 2 / v2 phai la:

- `AI co van dao sau`
- `AI lap lo trinh`
- `AI xuat bao cao`
