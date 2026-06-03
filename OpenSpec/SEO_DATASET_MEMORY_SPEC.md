# SEO DATASET MEMORY SPEC - AI Marketing Hub
<!-- Updated: 2026-06-03 -->

## 1. Muc tieu

Xay dung mot lop `SEO Dataset Memory` song song voi he thong hien tai de du an khong chi:
- doc du lieu hien tai
- phan tich tung lan

ma con co the:
- ghi nho nhung keyword tot
- ghi nho nhung pattern toi uu da co hieu qua
- ghi nho nhung recommendation da tung dua ra
- hoc tu ket qua thuc te theo thoi gian

Y tuong cot loi:

He thong khong duoc "tu hoc mo ho".
No phai co bo nho du lieu co cau truc, de:
- Advisor de xuat tot hon
- content planning dung huong hon
- SEO scoring va GEO readiness co context tot hon
- recommendation khong bi lap lai vo ich

## 2. Van de hien tai

Hien tai du an da co:
- GSC
- GA4
- SERP
- rank tracking
- technical SEO
- CWV
- schema validation
- broken links
- AI Advisor
- SEO Intelligence Data Layer

Nhung van con thieu 1 lop du lieu "tri nho SEO" de tra loi cac cau hoi:
- keyword nao tung la quick win tot that su?
- loai title nao da tung giup tang CTR?
- page type nao nen di voi schema nao?
- recommendation nao tung co ket qua tot?
- cluster keyword nao hop voi niche nay?
- intent nao thuong di kem format noi dung nao?

Neu khong co bo nho nay, he thong se:
- de xuat lai nhung thu da de xuat
- khong biet recommendation nao da tung hieu qua
- phu thuoc nhieu vao phan tich tung lan

## 3. Dinh vi dung

SEO Dataset Memory khong phai:
- vector DB
- raw data dump
- keyword list thu cong khong context

SEO Dataset Memory phai la:
- bo du lieu co cau truc
- co nguon goc
- co confidence
- co outcome neu co
- co the truy van de sinh recommendation tot hon

## 4. Muc tieu san pham

Lop nay se giup he thong lam duoc 4 viec tot hon:

### 4.1 Ghi nho keyword co gia tri

Khong chi luu keyword co impressions.
Can biet:
- keyword nao co CTR tot
- keyword nao tung la quick win
- keyword nao co conversion potential
- keyword nao hop voi tung page type

### 4.2 Ghi nho pattern thanh cong

Vi du:
- title pattern nao tang CTR
- meta description pattern nao hop local SEO
- FAQ pattern nao hop article
- schema combinations nao hop local business / product / article

### 4.3 Ghi nho ket qua recommendation

Neu Advisor tung de xuat:
- viet lai title
- them FAQ
- bo sung Organization schema

thi he thong can co kha nang luu:
- recommendation nao da dua ra
- da thuc hien hay chua
- ket qua sau khi thuc hien co tot len khong

### 4.4 Ho tro advisor va report

Advisor phase sau co the dua tren dataset memory de noi:
- "Voi nhom tu khoa local brand nay, title pattern X da tung hieu qua hon"
- "Voi page type service-local, FAQ + Organization schema + review block thuong la combo tot"
- "Recommendation nay da duoc dua ra 2 lan, chua duoc xu ly"

## 5. Nguyen tac du lieu

### 5.1 Khong luu mo ho

Khong luu kieu:
- `good_keywords = ["a", "b", "c"]`

Can luu co metadata:
- source
- niche
- page_type
- intent
- score
- confidence
- evidence

### 5.2 Tach 3 loai tri nho

Dataset memory nen tach thanh:

1. `Observed memory`
- du lieu tot da quan sat duoc

2. `Derived memory`
- pattern duoc tinh ra tu du lieu

3. `Recommendation memory`
- khuyen nghi da dua ra va outcome cua no

### 5.3 Khong coi "tot" la mot thu tuyet doi

Mot keyword tot phai phu thuoc:
- niche
- page type
- intent
- source
- timeframe

Vi du:
- keyword tot cho article co the khong tot cho homepage
- keyword CTR tot cho brand search khong giong keyword tot cho commercial intent

## 6. Cac nhom dataset de xay

### 6.1 Keyword intelligence memory

Luu cac thuoc tinh:
- keyword
- normalized_keyword
- site_url
- niche
- page_type
- search_intent
- source
- clicks
- impressions
- ctr
- avg_position
- trend_direction
- opportunity_type
- confidence
- observed_at

Vi du `opportunity_type`:
- quick_win
- high_ctr
- low_ctr_high_impression
- declining_rank
- new_opportunity

### 6.2 Content pattern memory

Luu:
- page_type
- intent
- heading_pattern
- title_pattern
- meta_pattern
- faq_present
- list_present
- table_present
- schema_types
- outcome_score
- confidence

Muc tieu:
- biet format noi dung nao hop voi loai page nao

### 6.3 Recommendation outcome memory

Luu:
- recommendation_type
- recommendation_text
- site_url
- page_url
- keyword
- created_at
- status
- outcome
- measured_delta
- reviewed_at

Vi du:
- doi title
- them FAQ
- sua schema
- bo sung internal links
- toi uu CWV

### 6.4 Entity / GEO memory

Luu:
- entity_type
- entity_name
- schema_combo
- trust_signals_present
- local_signals_present
- answerability_pattern
- geo_readiness_observed

### 6.5 Snippet / CTR memory

Luu:
- title_text
- meta_description_text
- title_pattern_label
- snippet_type
- keyword_cluster
- ctr_band
- position_band
- observed_effect

Muc tieu:
- tim pattern snippet co kha nang click tot hon

## 7. Data model de xuat

Phase dau khong nen qua nang.
Nên bat dau bang 4 bang chinh:

### 7.1 `seo_keyword_memory`

Chua:
- site_id
- site_url
- keyword
- normalized_keyword
- page_url
- page_type
- search_intent
- source
- clicks
- impressions
- ctr
- avg_position
- trend_direction
- opportunity_type
- confidence_score
- evidence_json
- observed_at

### 7.2 `seo_pattern_memory`

Chua:
- site_id
- niche
- page_type
- intent
- pattern_type
- pattern_label
- pattern_payload_json
- confidence_score
- outcome_score
- source_run_id
- observed_at

### 7.3 `seo_recommendation_outcomes`

Chua:
- site_id
- advisor_run_id
- recommendation_type
- recommendation_text
- page_url
- keyword
- status
- outcome
- measured_delta_json
- created_at
- reviewed_at

*Ghi chú Phase 1:*
- **Ranh giới:** `seo_rec_memory` lưu catalog khuyến nghị chiến lược tổng thể; còn `seo_recommendation_outcomes` lưu thực thể (instance) khuyến nghị phát sinh từ các advisor run để theo dõi trạng thái.
- **Strict Site Matching:** Giải quyết site thông qua chuẩn hóa URL/Domain nghiêm ngặt (loại bỏ protocol, `www.`, và trailing slash), không dùng khớp mờ.
- **Top Queries Filtering:** Lọc nhiễu GSC queries chỉ lưu vào Keyword Memory khi `clicks >= 5` hoặc `impressions >= 50`.
- **Safe Context Extraction:** Chỉ trích xuất `page_url` và `keyword` từ văn bản khuyến nghị khi khớp regex độ tin cậy cao, ngược lại để `NULL`.

### 7.4 `seo_dataset_tags`

Dung de gan nhan:
- local_seo
- service_page
- article
- quick_win
- schema_gap
- ctr_pattern
- faq_pattern

Co the dung bang phu de gan tag vao keyword/pattern/recommendation records.

## 8. Nguon sinh du lieu

### 8.1 Tu GSC

Sinh:
- keyword memory
- quick win memory
- low_ctr_high_impression memory

### 8.2 Tu GA4

Sinh:
- top page behavior memory
- engagement/bounce context

### 8.3 Tu SERP

Sinh:
- search intent memory
- title/snippet pattern memory
- competitor pattern memory

### 8.4 Tu Technical SEO / Schema / CWV

Sinh:
- issue memory
- remediation pattern memory
- schema combo memory

### 8.5 Tu AI Advisor

Sinh:
- recommendation outcome seeds
- action plan memory
- roadmap node memory

## 9. Cac use cases cu the

### 9.1 Advisor thong minh hon

Thay vi chi noi:
- "Ban nen toi uu title"

Advisor co the noi:
- "Voi nhom keyword local service nay, title pattern co trust signal + location thuong hieu qua hon trong du lieu da quan sat"

### 9.2 Content planner tot hon

Neu he thong thay:
- article intent informational
- keyword cluster co FAQ pattern hieu qua

thi planner co the goi y:
- outline theo mau da co ket qua tot

### 9.3 Report co gia tri hon

Report co the noi:
- "Recommendation nay da xuat hien 3 lan trong 45 ngay"
- "Quick win pattern nay da lap lai tren 4 keyword"

### 9.4 Feedback loop that su

Neu user danh dau recommendation da lam xong,
he thong co the theo doi:
- CTR co tang khong
- position co cai thien khong
- engagement co tot hon khong

## 10. Nguyen tac implementation

### 10.1 Khong lam full bo nho thong minh ngay

Phase 1 chi can:
- luu keyword memory
- luu recommendation outcome seed
- luu pattern memory co ban

### 10.2 Khong de AI ghi truc tiep vao memory khong kiem soat

AI chi nen de xuat.
Backend rules phai:
- validate
- gan source
- gan confidence
- luu co cau truc

### 10.3 Khong dung memory de thay the data goc

Memory la lop bo sung.
No khong thay:
- raw snapshots
- normalized entities
- derived signals

## 11. Tich hop voi he thong hien tai

SEO Dataset Memory nen noi vao:
- `backend/core/site_advisor.py`
- `backend/core/seo_intelligence.py`
- advisor run history
- recommendation memory
- data layer moi da co

Nó bo sung cho:
- `seo_raw_snapshots`
- `seo_advisor_runs`
- `seo_derived_signals`
- `seo_rec_memory`

Khong thay the cac bang nay.

## 12. Thu tu trien khai de xuat

### Phase 1
- tao spec va schema
- them `seo_keyword_memory`
- them `seo_recommendation_outcomes`
- ingest tu GSC quick wins + advisor action plans

### Phase 2
- them `seo_pattern_memory`
- rut title/snippet/schema/content patterns

### Phase 3
- them feedback loop
- danh dau recommendation da lam
- do delta KPI

### Phase 4
- cho Advisor truy van memory de recommendation tot hon

## 13. Definition of Done

Phase dau duoc coi la dat khi:

1. Co schema du lieu cho keyword memory va recommendation outcomes
2. AI Advisor co the ghi nho mot phan recommendation vao dataset memory
3. GSC quick wins co the duoc luu thanh keyword memory co metadata
4. Dataset memory khong la 1 bang JSON tong
5. Du lieu co source, confidence, timestamp, evidence

## 14. Khong duoc lam

- Khong luu "keyword tot" nhu 1 list text don gian
- Khong de AI tu gan nhan "tot" ma khong co evidence
- Khong nham dataset memory voi vector DB
- Khong mo ta he thong la "tu hoc" neu chua co feedback loop that
- Khong de recommendation memory va keyword memory bi trung vai tro

## 15. Ket luan

Y tuong "luu cac keyword tot va dataset de cai thien he thong" la dung,
nhung phai lam theo huong:

- co cau truc
- co bang chung
- co confidence
- co ngu canh
- co lich su

Neu lam dung, day se la mot trong nhung lop gia tri nhat cua du an,
vi no bien AI Marketing Hub tu:

- bo cong cu phan tich tung lan

thanh:

- he thong co tri nho SEO va recommendation memory theo thoi gian
