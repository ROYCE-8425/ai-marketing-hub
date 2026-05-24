import { useState } from "react";
import { API_BASE } from "../lib/apiConfig";

interface GeoBreakdown {
  score: number;
  max: number;
  details: {
    recommendations: string[];
    // eslint-disable-next-line @typescript-eslint/no-explicit-any -- API response data
    [key: string]: any;
  };
}

interface GeoResult {
  url: string;
  keyword: string;
  geo_score: number;
  grade: string;
  grade_label: string;
  breakdown: {
    schema: GeoBreakdown;
    structure: GeoBreakdown;
    eeat: GeoBreakdown;
    multimodal: GeoBreakdown;
    ai_visibility: GeoBreakdown;
  };
  recommendations: { category: string; recommendation: string }[];
  total_recommendations: number;
}

interface FaqItem {
  question: string;
  answer: string;
}

interface FaqResult {
  faqs: FaqItem[];
  schema_code: string;
  total_faqs: number;
}

const CATEGORY_META: Record<string, { icon: string; label: string; color: string }> = {
  schema: { icon: "🏗️", label: "Schema & Dữ liệu cấu trúc", color: "#16a34a" },
  structure: { icon: "📐", label: "Cấu trúc nội dung", color: "#3b82f6" },
  eeat: { icon: "🛡️", label: "E-E-A-T (Uy tín)", color: "#15803d" },
  multimodal: { icon: "🖼️", label: "Đa phương tiện", color: "#f59e0b" },
  ai_visibility: { icon: "🤖", label: "AI Visibility", color: "#ec4899" },
};

type SchemaTab = "local" | "organization" | "website" | "jobposting" | "event" | "howto" | "video" | "review";

const SCHEMA_TABS: { key: SchemaTab; icon: string; label: string }[] = [
  { key: "local", icon: "🏢", label: "LocalBusiness" },
  { key: "organization", icon: "🏛️", label: "Organization" },
  { key: "website", icon: "🌐", label: "WebSite" },
  { key: "jobposting", icon: "💼", label: "JobPosting" },
  { key: "event", icon: "🎪", label: "Event" },
  { key: "howto", icon: "📝", label: "HowTo" },
  { key: "video", icon: "🎬", label: "Video" },
  { key: "review", icon: "⭐", label: "Review" },
];

export function GeoOptimizer() {
  const [url, setUrl] = useState("");
  const [keyword, setKeyword] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<GeoResult | null>(null);
  const [error, setError] = useState("");

  // FAQ generator state
  const [faqLoading, setFaqLoading] = useState(false);
  const [faqResult, setFaqResult] = useState<FaqResult | null>(null);
  const [faqError, setFaqError] = useState("");
  const [showSchemaCode, setShowSchemaCode] = useState(false);
  const [codeCopied, setCodeCopied] = useState("");

  // Schema generator state
  const [showSchemaGen, setShowSchemaGen] = useState(false);
  const [activeSchemaTab, setActiveSchemaTab] = useState<SchemaTab>("local");
  const [schemaCode, setSchemaCode] = useState("");
  const [schemaLoading, setSchemaLoading] = useState(false);

  // LocalBusiness form
  const [schemaForm, setSchemaForm] = useState({
    name: "", address: "", phone: "", url: "", business_type: "LocalBusiness",
  });

  // Organization form
  const [orgForm, setOrgForm] = useState({
    name: "", url: "", logo_url: "", description: "", founder_name: "",
    email: "", phone: "", street: "", city: "", region: "", country: "VN",
    postal_code: "", social_profiles: "",
  });

  // WebSite form
  const [websiteForm, setWebsiteForm] = useState({
    name: "", url: "", description: "", search_url_template: "",
  });

  // JobPosting form
  const [jobForm, setJobForm] = useState({
    title: "", description: "", company_name: "", company_url: "",
    city: "", region: "", country: "VN",
    salary_min: 0, salary_max: 0, salary_currency: "VND",
    employment_type: "FULL_TIME", date_posted: "", valid_through: "", remote: false,
  });

  // Event form
  const [eventForm, setEventForm] = useState({
    name: "", description: "", start_date: "", end_date: "",
    location_name: "", location_address: "", url: "", image_url: "",
    performer_name: "", offers_price: 0, offers_currency: "VND", offers_url: "",
  });

  // HowTo form
  const [howtoForm, setHowtoForm] = useState({
    name: "", description: "", total_time: "",
    tools: "", supplies: "",
  });
  const [howtoSteps, setHowtoSteps] = useState([{ name: "", text: "", image_url: "" }]);

  // Video form
  const [videoForm, setVideoForm] = useState({
    name: "", description: "", thumbnail_url: "", upload_date: "",
    duration: "", content_url: "", embed_url: "",
  });

  // Review form
  const [reviewForm, setReviewForm] = useState({
    item_name: "", item_type: "Product", author_name: "",
    rating_value: 5, best_rating: 5, review_body: "", date_published: "",
  });

  const handleAnalyze = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!url.trim()) return;
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const r = await fetch(`${API_BASE}/geo/analyze`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: url.trim(), keyword: keyword.trim() }),
      });
      const d = await r.json();
      if (d.error) setError(d.error);
      else setResult(d);
    // eslint-disable-next-line @typescript-eslint/no-explicit-any -- API response data
    } catch (e: any) {
      setError(e.message || "Lỗi kết nối");
    }
    setLoading(false);
  };

  const handleGenerateFaq = async () => {
    setFaqLoading(true);
    setFaqError("");
    setFaqResult(null);
    try {
      const r = await fetch(`${API_BASE}/geo/generate-faq`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: url.trim() }),
      });
      const d = await r.json();
      if (d.error) setFaqError(d.error);
      else setFaqResult(d);
    // eslint-disable-next-line @typescript-eslint/no-explicit-any -- API response data
    } catch (e: any) {
      setFaqError(e.message || "Lỗi");
    }
    setFaqLoading(false);
  };

  const handleGenerateSchema = async () => {
    try {
      const r = await fetch(`${API_BASE}/geo/generate-schema`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(schemaForm),
      });
      const d = await r.json();
      if (d.schema_code) setSchemaCode(d.schema_code);
    } catch { /* ignore */ }
  };

  // eslint-disable-next-line @typescript-eslint/no-explicit-any -- API response data
  const generateAdvancedSchema = async (endpoint: string, body: any) => {
    setSchemaLoading(true);
    setSchemaCode("");
    try {
      const r = await fetch(`${API_BASE}/geo/${endpoint}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      const d = await r.json();
      if (d.html) setSchemaCode(d.html);
      else if (d.schema) setSchemaCode(JSON.stringify(d.schema, null, 2));
    } catch { /* ignore */ }
    setSchemaLoading(false);
  };

  const copyCode = (code: string, key: string = "main") => {
    navigator.clipboard.writeText(code);
    setCodeCopied(key);
    setTimeout(() => setCodeCopied(""), 2000);
  };

  const gradeColor = (grade: string) => {
    switch (grade) {
      case "A": return "#15803d";
      case "B": return "#3b82f6";
      case "C": return "#f59e0b";
      case "D": return "#ef4444";
      default: return "#ef4444";
    }
  };

  const addHowtoStep = () => setHowtoSteps([...howtoSteps, { name: "", text: "", image_url: "" }]);
  const removeHowtoStep = (idx: number) => setHowtoSteps(howtoSteps.filter((_, i) => i !== idx));
  const updateHowtoStep = (idx: number, field: string, value: string) => {
    const updated = [...howtoSteps];
    // eslint-disable-next-line @typescript-eslint/no-explicit-any -- API response data
    (updated[idx] as any)[field] = value;
    setHowtoSteps(updated);
  };

  const renderSchemaCodeBlock = () => {
    if (!schemaCode) return null;
    return (
      <div className="geo-code-block" style={{ marginTop: 12 }}>
        <div className="geo-code-header">
          <span>{'<script type="application/ld+json">'}</span>
          <button className="spin-copy-btn" onClick={() => copyCode(schemaCode, "schema")}>
            {codeCopied === "schema" ? "✅ Đã copy" : "📋 Copy"}
          </button>
        </div>
        <pre className="geo-code-pre">{schemaCode}</pre>
      </div>
    );
  };

  const renderSchemaTabContent = () => {
    switch (activeSchemaTab) {
      case "local":
        return (
          <div className="geo-schema-form">
            <div className="input-group">
              <label className="input-label">Tên doanh nghiệp</label>
              <input className="text-input" value={schemaForm.name}
                onChange={e => setSchemaForm({ ...schemaForm, name: e.target.value })} />
            </div>
            <div className="input-group">
              <label className="input-label">Địa chỉ</label>
              <input className="text-input" value={schemaForm.address}
                onChange={e => setSchemaForm({ ...schemaForm, address: e.target.value })} />
            </div>
            <div className="input-group">
              <label className="input-label">Số điện thoại</label>
              <input className="text-input" value={schemaForm.phone}
                onChange={e => setSchemaForm({ ...schemaForm, phone: e.target.value })} />
            </div>
            <div className="input-group">
              <label className="input-label">Loại hình</label>
              <select className="text-input" value={schemaForm.business_type}
                onChange={e => setSchemaForm({ ...schemaForm, business_type: e.target.value })}
                style={{ paddingLeft: 12 }}>
                <option value="AutoDealer">Đại lý ô tô</option>
                <option value="LocalBusiness">Doanh nghiệp địa phương</option>
                <option value="Store">Cửa hàng</option>
                <option value="Restaurant">Nhà hàng</option>
                <option value="MedicalBusiness">Y tế</option>
              </select>
            </div>
            <button className="rt-btn rt-btn-add" onClick={handleGenerateSchema}>⚡ Tạo Schema</button>
          </div>
        );

      case "organization":
        return (
          <div className="geo-schema-form">
            <div className="schema-form-grid">
              <div className="input-group">
                <label className="input-label">Tên tổ chức *</label>
                <input className="text-input" value={orgForm.name} placeholder="Công ty ABC"
                  onChange={e => setOrgForm({ ...orgForm, name: e.target.value })} />
              </div>
              <div className="input-group">
                <label className="input-label">Website URL</label>
                <input className="text-input" value={orgForm.url} placeholder="https://example.com"
                  onChange={e => setOrgForm({ ...orgForm, url: e.target.value })} />
              </div>
              <div className="input-group">
                <label className="input-label">Logo URL</label>
                <input className="text-input" value={orgForm.logo_url} placeholder="https://example.com/logo.png"
                  onChange={e => setOrgForm({ ...orgForm, logo_url: e.target.value })} />
              </div>
              <div className="input-group">
                <label className="input-label">Mô tả</label>
                <input className="text-input" value={orgForm.description}
                  onChange={e => setOrgForm({ ...orgForm, description: e.target.value })} />
              </div>
              <div className="input-group">
                <label className="input-label">Người sáng lập</label>
                <input className="text-input" value={orgForm.founder_name}
                  onChange={e => setOrgForm({ ...orgForm, founder_name: e.target.value })} />
              </div>
              <div className="input-group">
                <label className="input-label">Email</label>
                <input className="text-input" value={orgForm.email} type="email"
                  onChange={e => setOrgForm({ ...orgForm, email: e.target.value })} />
              </div>
              <div className="input-group">
                <label className="input-label">Số điện thoại</label>
                <input className="text-input" value={orgForm.phone}
                  onChange={e => setOrgForm({ ...orgForm, phone: e.target.value })} />
              </div>
              <div className="input-group">
                <label className="input-label">Địa chỉ (đường)</label>
                <input className="text-input" value={orgForm.street}
                  onChange={e => setOrgForm({ ...orgForm, street: e.target.value })} />
              </div>
              <div className="input-group">
                <label className="input-label">Thành phố</label>
                <input className="text-input" value={orgForm.city}
                  onChange={e => setOrgForm({ ...orgForm, city: e.target.value })} />
              </div>
              <div className="input-group">
                <label className="input-label">Vùng/Tỉnh</label>
                <input className="text-input" value={orgForm.region}
                  onChange={e => setOrgForm({ ...orgForm, region: e.target.value })} />
              </div>
              <div className="input-group">
                <label className="input-label">Quốc gia</label>
                <input className="text-input" value={orgForm.country}
                  onChange={e => setOrgForm({ ...orgForm, country: e.target.value })} />
              </div>
              <div className="input-group">
                <label className="input-label">Mã bưu điện</label>
                <input className="text-input" value={orgForm.postal_code}
                  onChange={e => setOrgForm({ ...orgForm, postal_code: e.target.value })} />
              </div>
            </div>
            <div className="input-group" style={{ marginTop: 8 }}>
              <label className="input-label">Mạng xã hội (mỗi URL 1 dòng)</label>
              <textarea className="text-input" rows={3} value={orgForm.social_profiles}
                placeholder={"https://facebook.com/company\nhttps://linkedin.com/company/abc"}
                onChange={e => setOrgForm({ ...orgForm, social_profiles: e.target.value })}
                style={{ resize: "vertical", minHeight: 60 }} />
            </div>
            <button className="rt-btn rt-btn-add" disabled={!orgForm.name || schemaLoading}
              onClick={() => generateAdvancedSchema("generate-organization-schema", {
                ...orgForm,
                social_profiles: orgForm.social_profiles ? orgForm.social_profiles.split("\n").filter(Boolean) : [],
              })}>
              {schemaLoading ? "⏳ Đang tạo..." : "⚡ Tạo Schema"}
            </button>
          </div>
        );

      case "website":
        return (
          <div className="geo-schema-form">
            <div className="schema-form-grid">
              <div className="input-group">
                <label className="input-label">Tên website *</label>
                <input className="text-input" value={websiteForm.name} placeholder="AI Marketing Hub"
                  onChange={e => setWebsiteForm({ ...websiteForm, name: e.target.value })} />
              </div>
              <div className="input-group">
                <label className="input-label">URL</label>
                <input className="text-input" value={websiteForm.url} placeholder="https://example.com"
                  onChange={e => setWebsiteForm({ ...websiteForm, url: e.target.value })} />
              </div>
              <div className="input-group">
                <label className="input-label">Mô tả</label>
                <input className="text-input" value={websiteForm.description}
                  onChange={e => setWebsiteForm({ ...websiteForm, description: e.target.value })} />
              </div>
              <div className="input-group">
                <label className="input-label">Search URL Template</label>
                <input className="text-input" value={websiteForm.search_url_template}
                  placeholder="https://example.com/search?q={search_term_string}"
                  onChange={e => setWebsiteForm({ ...websiteForm, search_url_template: e.target.value })} />
              </div>
            </div>
            <button className="rt-btn rt-btn-add" disabled={!websiteForm.name || schemaLoading}
              onClick={() => generateAdvancedSchema("generate-website-schema", websiteForm)}>
              {schemaLoading ? "⏳ Đang tạo..." : "⚡ Tạo Schema"}
            </button>
          </div>
        );

      case "jobposting":
        return (
          <div className="geo-schema-form">
            <div className="schema-form-grid">
              <div className="input-group">
                <label className="input-label">Vị trí tuyển dụng *</label>
                <input className="text-input" value={jobForm.title} placeholder="Frontend Developer"
                  onChange={e => setJobForm({ ...jobForm, title: e.target.value })} />
              </div>
              <div className="input-group">
                <label className="input-label">Tên công ty</label>
                <input className="text-input" value={jobForm.company_name}
                  onChange={e => setJobForm({ ...jobForm, company_name: e.target.value })} />
              </div>
              <div className="input-group">
                <label className="input-label">Website công ty</label>
                <input className="text-input" value={jobForm.company_url}
                  onChange={e => setJobForm({ ...jobForm, company_url: e.target.value })} />
              </div>
              <div className="input-group">
                <label className="input-label">Loại hình</label>
                <select className="text-input" value={jobForm.employment_type}
                  onChange={e => setJobForm({ ...jobForm, employment_type: e.target.value })}
                  style={{ paddingLeft: 12 }}>
                  <option value="FULL_TIME">Toàn thời gian</option>
                  <option value="PART_TIME">Bán thời gian</option>
                  <option value="CONTRACTOR">Hợp đồng</option>
                  <option value="INTERN">Thực tập</option>
                </select>
              </div>
              <div className="input-group">
                <label className="input-label">Thành phố</label>
                <input className="text-input" value={jobForm.city}
                  onChange={e => setJobForm({ ...jobForm, city: e.target.value })} />
              </div>
              <div className="input-group">
                <label className="input-label">Vùng/Tỉnh</label>
                <input className="text-input" value={jobForm.region}
                  onChange={e => setJobForm({ ...jobForm, region: e.target.value })} />
              </div>
              <div className="input-group">
                <label className="input-label">Lương tối thiểu</label>
                <input className="text-input" type="number" value={jobForm.salary_min || ""}
                  onChange={e => setJobForm({ ...jobForm, salary_min: Number(e.target.value) })} />
              </div>
              <div className="input-group">
                <label className="input-label">Lương tối đa</label>
                <input className="text-input" type="number" value={jobForm.salary_max || ""}
                  onChange={e => setJobForm({ ...jobForm, salary_max: Number(e.target.value) })} />
              </div>
              <div className="input-group">
                <label className="input-label">Đơn vị tiền</label>
                <input className="text-input" value={jobForm.salary_currency}
                  onChange={e => setJobForm({ ...jobForm, salary_currency: e.target.value })} />
              </div>
              <div className="input-group">
                <label className="input-label">Ngày đăng</label>
                <input className="text-input" type="date" value={jobForm.date_posted}
                  onChange={e => setJobForm({ ...jobForm, date_posted: e.target.value })} />
              </div>
              <div className="input-group">
                <label className="input-label">Hạn nộp</label>
                <input className="text-input" type="date" value={jobForm.valid_through}
                  onChange={e => setJobForm({ ...jobForm, valid_through: e.target.value })} />
              </div>
              <div className="input-group" style={{ display: "flex", alignItems: "center", gap: 8 }}>
                <input type="checkbox" id="remote-check" checked={jobForm.remote}
                  onChange={e => setJobForm({ ...jobForm, remote: e.target.checked })} />
                <label htmlFor="remote-check" className="input-label" style={{ marginBottom: 0 }}>Làm việc từ xa</label>
              </div>
            </div>
            <div className="input-group" style={{ marginTop: 8 }}>
              <label className="input-label">Mô tả công việc</label>
              <textarea className="text-input" rows={3} value={jobForm.description}
                onChange={e => setJobForm({ ...jobForm, description: e.target.value })}
                style={{ resize: "vertical", minHeight: 60 }} />
            </div>
            <button className="rt-btn rt-btn-add" disabled={!jobForm.title || schemaLoading}
              onClick={() => generateAdvancedSchema("generate-jobposting-schema", jobForm)}>
              {schemaLoading ? "⏳ Đang tạo..." : "⚡ Tạo Schema"}
            </button>
          </div>
        );

      case "event":
        return (
          <div className="geo-schema-form">
            <div className="schema-form-grid">
              <div className="input-group">
                <label className="input-label">Tên sự kiện *</label>
                <input className="text-input" value={eventForm.name} placeholder="Hội thảo SEO 2026"
                  onChange={e => setEventForm({ ...eventForm, name: e.target.value })} />
              </div>
              <div className="input-group">
                <label className="input-label">URL sự kiện</label>
                <input className="text-input" value={eventForm.url}
                  onChange={e => setEventForm({ ...eventForm, url: e.target.value })} />
              </div>
              <div className="input-group">
                <label className="input-label">Ngày bắt đầu</label>
                <input className="text-input" type="datetime-local" value={eventForm.start_date}
                  onChange={e => setEventForm({ ...eventForm, start_date: e.target.value })} />
              </div>
              <div className="input-group">
                <label className="input-label">Ngày kết thúc</label>
                <input className="text-input" type="datetime-local" value={eventForm.end_date}
                  onChange={e => setEventForm({ ...eventForm, end_date: e.target.value })} />
              </div>
              <div className="input-group">
                <label className="input-label">Tên địa điểm</label>
                <input className="text-input" value={eventForm.location_name}
                  onChange={e => setEventForm({ ...eventForm, location_name: e.target.value })} />
              </div>
              <div className="input-group">
                <label className="input-label">Địa chỉ</label>
                <input className="text-input" value={eventForm.location_address}
                  onChange={e => setEventForm({ ...eventForm, location_address: e.target.value })} />
              </div>
              <div className="input-group">
                <label className="input-label">Hình ảnh URL</label>
                <input className="text-input" value={eventForm.image_url}
                  onChange={e => setEventForm({ ...eventForm, image_url: e.target.value })} />
              </div>
              <div className="input-group">
                <label className="input-label">Người biểu diễn/diễn giả</label>
                <input className="text-input" value={eventForm.performer_name}
                  onChange={e => setEventForm({ ...eventForm, performer_name: e.target.value })} />
              </div>
              <div className="input-group">
                <label className="input-label">Giá vé</label>
                <input className="text-input" type="number" value={eventForm.offers_price || ""}
                  onChange={e => setEventForm({ ...eventForm, offers_price: Number(e.target.value) })} />
              </div>
              <div className="input-group">
                <label className="input-label">Đơn vị tiền</label>
                <input className="text-input" value={eventForm.offers_currency}
                  onChange={e => setEventForm({ ...eventForm, offers_currency: e.target.value })} />
              </div>
              <div className="input-group">
                <label className="input-label">URL mua vé</label>
                <input className="text-input" value={eventForm.offers_url}
                  onChange={e => setEventForm({ ...eventForm, offers_url: e.target.value })} />
              </div>
            </div>
            <div className="input-group" style={{ marginTop: 8 }}>
              <label className="input-label">Mô tả sự kiện</label>
              <textarea className="text-input" rows={3} value={eventForm.description}
                onChange={e => setEventForm({ ...eventForm, description: e.target.value })}
                style={{ resize: "vertical", minHeight: 60 }} />
            </div>
            <button className="rt-btn rt-btn-add" disabled={!eventForm.name || schemaLoading}
              onClick={() => generateAdvancedSchema("generate-event-schema", eventForm)}>
              {schemaLoading ? "⏳ Đang tạo..." : "⚡ Tạo Schema"}
            </button>
          </div>
        );

      case "howto":
        return (
          <div className="geo-schema-form">
            <div className="schema-form-grid">
              <div className="input-group">
                <label className="input-label">Tên hướng dẫn *</label>
                <input className="text-input" value={howtoForm.name} placeholder="Cách tối ưu SEO on-page"
                  onChange={e => setHowtoForm({ ...howtoForm, name: e.target.value })} />
              </div>
              <div className="input-group">
                <label className="input-label">Tổng thời gian (ISO 8601)</label>
                <input className="text-input" value={howtoForm.total_time} placeholder="PT30M"
                  onChange={e => setHowtoForm({ ...howtoForm, total_time: e.target.value })} />
              </div>
            </div>
            <div className="input-group" style={{ marginTop: 8 }}>
              <label className="input-label">Mô tả</label>
              <textarea className="text-input" rows={2} value={howtoForm.description}
                onChange={e => setHowtoForm({ ...howtoForm, description: e.target.value })}
                style={{ resize: "vertical" }} />
            </div>
            <div className="input-group">
              <label className="input-label">Công cụ (mỗi dòng 1 công cụ)</label>
              <textarea className="text-input" rows={2} value={howtoForm.tools}
                placeholder={"Google Search Console\nAhrefs"}
                onChange={e => setHowtoForm({ ...howtoForm, tools: e.target.value })}
                style={{ resize: "vertical" }} />
            </div>
            <div className="input-group">
              <label className="input-label">Nguyên liệu/Vật liệu (mỗi dòng 1 mục)</label>
              <textarea className="text-input" rows={2} value={howtoForm.supplies}
                onChange={e => setHowtoForm({ ...howtoForm, supplies: e.target.value })}
                style={{ resize: "vertical" }} />
            </div>

            <div className="howto-steps-section">
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8 }}>
                <label className="input-label" style={{ marginBottom: 0, fontWeight: 600 }}>Các bước thực hiện</label>
                <button className="rt-btn rt-btn-add" style={{ padding: "4px 12px", fontSize: 13 }} onClick={addHowtoStep}>+ Thêm bước</button>
              </div>
              {howtoSteps.map((step, idx) => (
                <div key={idx} className="howto-step-row">
                  <span className="howto-step-num">#{idx + 1}</span>
                  <input className="text-input" placeholder="Tên bước" value={step.name}
                    onChange={e => updateHowtoStep(idx, "name", e.target.value)}
                    style={{ flex: 1 }} />
                  <input className="text-input" placeholder="Mô tả chi tiết" value={step.text}
                    onChange={e => updateHowtoStep(idx, "text", e.target.value)}
                    style={{ flex: 2 }} />
                  <input className="text-input" placeholder="URL hình (tuỳ chọn)" value={step.image_url}
                    onChange={e => updateHowtoStep(idx, "image_url", e.target.value)}
                    style={{ flex: 1 }} />
                  {howtoSteps.length > 1 && (
                    <button className="rt-btn" style={{ padding: "4px 8px", fontSize: 12, background: "#ef4444", color: "#fff" }}
                      onClick={() => removeHowtoStep(idx)}>✕</button>
                  )}
                </div>
              ))}
            </div>

            <button className="rt-btn rt-btn-add" disabled={!howtoForm.name || schemaLoading}
              onClick={() => generateAdvancedSchema("generate-howto-schema", {
                name: howtoForm.name,
                description: howtoForm.description,
                total_time: howtoForm.total_time,
                steps: howtoSteps.filter(s => s.name || s.text),
                tools: howtoForm.tools ? howtoForm.tools.split("\n").filter(Boolean) : [],
                supplies: howtoForm.supplies ? howtoForm.supplies.split("\n").filter(Boolean) : [],
              })}>
              {schemaLoading ? "⏳ Đang tạo..." : "⚡ Tạo Schema"}
            </button>
          </div>
        );

      case "video":
        return (
          <div className="geo-schema-form">
            <div className="schema-form-grid">
              <div className="input-group">
                <label className="input-label">Tên video *</label>
                <input className="text-input" value={videoForm.name} placeholder="Hướng dẫn SEO 2026"
                  onChange={e => setVideoForm({ ...videoForm, name: e.target.value })} />
              </div>
              <div className="input-group">
                <label className="input-label">Thumbnail URL</label>
                <input className="text-input" value={videoForm.thumbnail_url}
                  onChange={e => setVideoForm({ ...videoForm, thumbnail_url: e.target.value })} />
              </div>
              <div className="input-group">
                <label className="input-label">Ngày upload</label>
                <input className="text-input" type="date" value={videoForm.upload_date}
                  onChange={e => setVideoForm({ ...videoForm, upload_date: e.target.value })} />
              </div>
              <div className="input-group">
                <label className="input-label">Thời lượng (ISO 8601)</label>
                <input className="text-input" value={videoForm.duration} placeholder="PT5M30S"
                  onChange={e => setVideoForm({ ...videoForm, duration: e.target.value })} />
              </div>
              <div className="input-group">
                <label className="input-label">Content URL</label>
                <input className="text-input" value={videoForm.content_url}
                  onChange={e => setVideoForm({ ...videoForm, content_url: e.target.value })} />
              </div>
              <div className="input-group">
                <label className="input-label">Embed URL</label>
                <input className="text-input" value={videoForm.embed_url}
                  onChange={e => setVideoForm({ ...videoForm, embed_url: e.target.value })} />
              </div>
            </div>
            <div className="input-group" style={{ marginTop: 8 }}>
              <label className="input-label">Mô tả</label>
              <textarea className="text-input" rows={3} value={videoForm.description}
                onChange={e => setVideoForm({ ...videoForm, description: e.target.value })}
                style={{ resize: "vertical", minHeight: 60 }} />
            </div>
            <button className="rt-btn rt-btn-add" disabled={!videoForm.name || schemaLoading}
              onClick={() => generateAdvancedSchema("generate-video-schema", videoForm)}>
              {schemaLoading ? "⏳ Đang tạo..." : "⚡ Tạo Schema"}
            </button>
          </div>
        );

      case "review":
        return (
          <div className="geo-schema-form">
            <div className="schema-form-grid">
              <div className="input-group">
                <label className="input-label">Tên sản phẩm/doanh nghiệp *</label>
                <input className="text-input" value={reviewForm.item_name}
                  onChange={e => setReviewForm({ ...reviewForm, item_name: e.target.value })} />
              </div>
              <div className="input-group">
                <label className="input-label">Loại</label>
                <select className="text-input" value={reviewForm.item_type}
                  onChange={e => setReviewForm({ ...reviewForm, item_type: e.target.value })}
                  style={{ paddingLeft: 12 }}>
                  <option value="Product">Sản phẩm</option>
                  <option value="LocalBusiness">Doanh nghiệp</option>
                  <option value="Organization">Tổ chức</option>
                </select>
              </div>
              <div className="input-group">
                <label className="input-label">Tên tác giả</label>
                <input className="text-input" value={reviewForm.author_name}
                  onChange={e => setReviewForm({ ...reviewForm, author_name: e.target.value })} />
              </div>
              <div className="input-group">
                <label className="input-label">Điểm đánh giá</label>
                <input className="text-input" type="number" step="0.1" min="0" max="5" value={reviewForm.rating_value}
                  onChange={e => setReviewForm({ ...reviewForm, rating_value: Number(e.target.value) })} />
              </div>
              <div className="input-group">
                <label className="input-label">Điểm tối đa</label>
                <input className="text-input" type="number" value={reviewForm.best_rating}
                  onChange={e => setReviewForm({ ...reviewForm, best_rating: Number(e.target.value) })} />
              </div>
              <div className="input-group">
                <label className="input-label">Ngày đăng</label>
                <input className="text-input" type="date" value={reviewForm.date_published}
                  onChange={e => setReviewForm({ ...reviewForm, date_published: e.target.value })} />
              </div>
            </div>
            <div className="input-group" style={{ marginTop: 8 }}>
              <label className="input-label">Nội dung đánh giá</label>
              <textarea className="text-input" rows={3} value={reviewForm.review_body}
                onChange={e => setReviewForm({ ...reviewForm, review_body: e.target.value })}
                style={{ resize: "vertical", minHeight: 60 }} />
            </div>
            <button className="rt-btn rt-btn-add" disabled={!reviewForm.item_name || schemaLoading}
              onClick={() => generateAdvancedSchema("generate-review-schema", reviewForm)}>
              {schemaLoading ? "⏳ Đang tạo..." : "⚡ Tạo Schema"}
            </button>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="geo-optimizer">
      <form className="audit-form" onSubmit={handleAnalyze}>
        <div className="hint-box">
          🤖 <strong>GEO — Generative Engine Optimization:</strong> Kiểm tra mức độ
          "AI-friendly" + tạo FAQ Schema + Bộ Schema.org nâng cao cho website.
        </div>

        <div className="input-row">
          <div className="input-group" style={{ flex: 2 }}>
            <label className="input-label">URL trang web</label>
            <div className="input-wrap">
              <svg className="input-icon" width="18" height="18" viewBox="0 0 24 24"
                fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0z" />
                <path d="M3.6 9h16.8M3.6 15h16.8" />
              </svg>
              <input type="url" className="text-input" placeholder="https://example.com"
                value={url} onChange={e => setUrl(e.target.value)} required />
            </div>
          </div>

          <div className="input-group" style={{ flex: 1 }}>
            <label className="input-label">Từ khóa chính</label>
            <div className="input-wrap">
              <svg className="input-icon" width="18" height="18" viewBox="0 0 24 24"
                fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="11" cy="11" r="8" /><path d="m21 21-4.35-4.35" />
              </svg>
              <input type="text" className="text-input" placeholder="từ khóa..."
                value={keyword} onChange={e => setKeyword(e.target.value)} />
            </div>
          </div>

          <button className={`submit-btn ${loading ? "loading" : ""}`}
            type="submit" disabled={loading || !url.trim()} style={{ alignSelf: "flex-end" }}>
            {loading ? (
              <><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" className="spin-icon">
                <path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8" /></svg> Đang phân tích...</>
            ) : (
              <><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                <path d="M12 2L2 7l10 5 10-5-10-5z" /><path d="M2 17l10 5 10-5" /><path d="M2 12l10 5 10-5" /></svg> Phân tích GEO</>
            )}
          </button>
        </div>

        {error && <p className="error-msg" role="alert">{error}</p>}
      </form>

      {result && (
        <div className="geo-result">
          {/* Score hero */}
          <div className="geo-score-hero">
            <div className="geo-score-ring">
              <svg viewBox="0 0 120 120" width="140" height="140">
                <circle cx="60" cy="60" r="52" fill="none" stroke="rgba(0,0,0,0.05)" strokeWidth="8" />
                <circle cx="60" cy="60" r="52" fill="none" stroke={gradeColor(result.grade)}
                  strokeWidth="8" strokeLinecap="round"
                  strokeDasharray={`${(result.geo_score / 100) * 327} 327`}
                  transform="rotate(-90 60 60)" style={{ transition: "stroke-dasharray 1s ease" }} />
              </svg>
              <div className="geo-score-inner">
                <span className="geo-score-num">{result.geo_score}</span>
                <span className="geo-score-max">/100</span>
              </div>
            </div>
            <div className="geo-score-info">
              <span className="geo-grade" style={{ color: gradeColor(result.grade) }}>{result.grade}</span>
              <span className="geo-grade-label">{result.grade_label}</span>
              <p className="geo-url">{result.url}</p>
            </div>
          </div>

          {/* Breakdown */}
          <div className="geo-breakdown">
            <h3 className="section-title">📊 Chi tiết điểm GEO</h3>
            <div className="geo-bars">
              {Object.entries(result.breakdown).map(([key, val]) => {
                const meta = CATEGORY_META[key] || { icon: "📌", label: key, color: "#888" };
                const pct = (val.score / val.max) * 100;
                return (
                  <div key={key} className="geo-bar-item">
                    <div className="geo-bar-label">
                      <span>{meta.icon} {meta.label}</span>
                      <span style={{ color: meta.color, fontWeight: 700 }}>{val.score}/{val.max}</span>
                    </div>
                    <div className="geo-bar-track">
                      <div className="geo-bar-fill" style={{ width: `${pct}%`, background: meta.color }} />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Recommendations */}
          <div className="geo-recs">
            <h3 className="section-title">💡 Khuyến nghị ({result.total_recommendations})</h3>
            <div className="geo-recs-list">
              {result.recommendations.map((rec, i) => (
                <div key={i} className="geo-rec-item">
                  <span className="geo-rec-category">{rec.category}</span>
                  <span className="geo-rec-text">{rec.recommendation}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Action buttons: FAQ + Schema */}
          <div className="geo-actions">
            <button className="rt-btn rt-btn-add" onClick={handleGenerateFaq} disabled={faqLoading}>
              {faqLoading ? "⏳ Đang tạo FAQ..." : "🤖 Tạo FAQ Schema từ AI"}
            </button>
            <button className="rt-btn rt-btn-sync" onClick={() => setShowSchemaGen(!showSchemaGen)}>
              {showSchemaGen ? "✕ Đóng Schema Generator" : "🏗️ Mở bộ tạo Schema nâng cao"}
            </button>
          </div>

          {/* FAQ Result */}
          {faqError && <p className="error-msg">{faqError}</p>}
          {faqResult && (
            <div className="geo-faq-result">
              <h3 className="section-title">❓ FAQ Schema ({faqResult.total_faqs} câu hỏi)</h3>
              <div className="geo-faq-list">
                {faqResult.faqs.map((faq, i) => (
                  <div key={i} className="geo-faq-item">
                    <div className="geo-faq-q">❓ {faq.question}</div>
                    <div className="geo-faq-a">{faq.answer}</div>
                  </div>
                ))}
              </div>
              <div className="geo-code-section">
                <button className="spin-view-btn active" onClick={() => setShowSchemaCode(!showSchemaCode)}>
                  {showSchemaCode ? "Ẩn code" : "📋 Xem JSON-LD code"}
                </button>
                {showSchemaCode && (
                  <div className="geo-code-block">
                    <div className="geo-code-header">
                      <span>{'<script type="application/ld+json">'}</span>
                      <button className="spin-copy-btn" onClick={() => copyCode(faqResult.schema_code, "faq")}>
                        {codeCopied === "faq" ? "✅ Đã copy" : "📋 Copy"}
                      </button>
                    </div>
                    <pre className="geo-code-pre">{faqResult.schema_code}</pre>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Advanced Schema Generator with tabs */}
          {showSchemaGen && (
            <div className="geo-schema-gen">
              <h3 className="section-title">🏗️ Bộ tạo Schema.org nâng cao</h3>
              <div className="schema-tabs">
                {SCHEMA_TABS.map(tab => (
                  <button key={tab.key}
                    className={`schema-tab-btn ${activeSchemaTab === tab.key ? "active" : ""}`}
                    onClick={() => { setActiveSchemaTab(tab.key); setSchemaCode(""); }}>
                    <span className="schema-tab-icon">{tab.icon}</span>
                    <span className="schema-tab-label">{tab.label}</span>
                  </button>
                ))}
              </div>
              <div className="schema-tab-content">
                {renderSchemaTabContent()}
                {renderSchemaCodeBlock()}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Standalone schema generator — works even without running GEO analysis */}
      {!result && (
        <div style={{ marginTop: 16 }}>
          <button className="rt-btn rt-btn-sync" onClick={() => setShowSchemaGen(!showSchemaGen)}>
            {showSchemaGen ? "✕ Đóng Schema Generator" : "🏗️ Mở bộ tạo Schema nâng cao"}
          </button>
          {showSchemaGen && (
            <div className="geo-schema-gen" style={{ marginTop: 12 }}>
              <h3 className="section-title">🏗️ Bộ tạo Schema.org nâng cao</h3>
              <div className="schema-tabs">
                {SCHEMA_TABS.map(tab => (
                  <button key={tab.key}
                    className={`schema-tab-btn ${activeSchemaTab === tab.key ? "active" : ""}`}
                    onClick={() => { setActiveSchemaTab(tab.key); setSchemaCode(""); }}>
                    <span className="schema-tab-icon">{tab.icon}</span>
                    <span className="schema-tab-label">{tab.label}</span>
                  </button>
                ))}
              </div>
              <div className="schema-tab-content">
                {renderSchemaTabContent()}
                {renderSchemaCodeBlock()}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
