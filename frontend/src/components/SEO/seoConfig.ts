// Centralized SEO metadata for every route/tab

export interface PageSEO {
  title: string;
  description: string;
  path: string;
}

export const SEO_CONFIG: Record<string, PageSEO> = {
  dashboard: {
    title: 'Tổng quan',
    description: 'Bảng điều khiển tổng quan AI Marketing Hub — theo dõi hiệu suất SEO, traffic, và các chỉ số marketing quan trọng.',
    path: '/',
  },
  seo: {
    title: 'Kiểm tra SEO',
    description: 'Công cụ kiểm tra SEO on-page — phân tích keyword density, chất lượng nội dung, LSI keywords và điểm SEO.',
    path: '/seo-audit',
  },
  techseo: {
    title: 'Technical SEO',
    description: 'Quét Technical SEO — kiểm tra meta tags, headings, hình ảnh, mobile, links, sitemap, hiệu suất, bảo mật.',
    path: '/technical-seo',
  },
  cro: {
    title: 'CRO & Trust',
    description: 'Phân tích CRO (Conversion Rate Optimization) — checklist CRO, CTA analysis, trust signals, above-fold analysis.',
    path: '/cro',
  },
  serp: {
    title: 'SERP Live',
    description: 'Kết quả tìm kiếm SERP trực tiếp — theo dõi vị trí từ khóa trên Google theo thời gian thực.',
    path: '/serp',
  },
  backlinks: {
    title: 'Phân tích Backlinks',
    description: 'Phân tích backlinks — kiểm tra liên kết nội bộ, liên kết bên ngoài, anchor text.',
    path: '/backlinks',
  },
  ranktracker: {
    title: 'Theo dõi thứ hạng',
    description: 'Theo dõi thứ hạng từ khóa — import CSV, sync GSC, alerts khi tụt hạng, export Excel.',
    path: '/rank-tracker',
  },
  aikeys: {
    title: 'Phân tích từ khóa AI',
    description: 'Phân tích từ khóa bằng AI — clustering, TF-IDF, search intent, Google Search Console data.',
    path: '/keywords',
  },
  competitor: {
    title: 'Phân tích đối thủ',
    description: 'Phân tích gap đối thủ cạnh tranh — so sánh nội dung, tìm khoảng trống, xây dựng chiến lược.',
    path: '/competitor',
  },
  planner: {
    title: 'Lập kế hoạch nội dung AI',
    description: 'Lập kế hoạch nội dung bằng AI — tạo outline, section planning, meta tags, engagement distribution.',
    path: '/content-planner',
  },
  spineditor: {
    title: 'Spin Editor',
    description: 'Spin Editor — viết lại nội dung AI với 4 giọng văn, 3 mức độ, bảo toàn từ khóa.',
    path: '/spin-editor',
  },
  geo: {
    title: 'GEO Optimizer',
    description: 'Generative Engine Optimization — tối ưu cho AI search engines (SGE, Bing Chat, Perplexity), E-E-A-T, Schema generators.',
    path: '/geo-optimizer',
  },
  calendar: {
    title: 'Lịch nội dung',
    description: 'Quản lý lịch nội dung — lên lịch xuất bản, theo dõi trạng thái, gợi ý chủ đề AI.',
    path: '/content-calendar',
  },
  abtest: {
    title: 'A/B Testing SEO',
    description: 'A/B Testing SEO — so sánh 2 phiên bản title, description, heading, nội dung với AI evaluation.',
    path: '/ab-testing',
  },
  report: {
    title: 'Báo cáo AI',
    description: 'Tạo báo cáo SEO toàn diện bằng AI — phân tích chi tiết và đề xuất cải thiện.',
    path: '/report',
  },
  tracker: {
    title: 'Campaign Tracker',
    description: 'Theo dõi chiến dịch marketing — opportunity scoring 8 yếu tố, search intent, traffic projection.',
    path: '/campaign',
  },
  fileconvert: {
    title: 'Chuyển đổi file',
    description: 'Chuyển đổi file sang Markdown — hỗ trợ PDF, Word, Excel, PPT với phân tích SEO.',
    path: '/file-converter',
  },
  sites: {
    title: 'Quản lý website',
    description: 'Quản lý nhiều website — thêm, xóa, chuyển đổi giữa các site.',
    path: '/sites',
  },
  googlesetup: {
    title: 'Cấu hình Google',
    description: 'Kết nối Google Search Console và Google Analytics — OAuth2, API keys.',
    path: '/google-setup',
  },
  cwv: {
    title: 'Core Web Vitals',
    description: 'Kiểm tra Core Web Vitals — LCP, INP, CLS, điểm Performance, SEO, Accessibility từ Google PageSpeed.',
    path: '/core-web-vitals',
  },
  brokenlinks: {
    title: 'Kiểm tra link hỏng',
    description: 'Quét website tìm link hỏng, 404, redirect — phân loại link nội bộ và bên ngoài.',
    path: '/broken-links',
  },
  schemavalidator: {
    title: 'Xác thực Schema',
    description: 'Xác thực JSON-LD structured data trên trang web — kiểm tra Schema.org, tìm lỗi và cảnh báo.',
    path: '/schema-validator',
  },
  login: {
    title: 'Đăng nhập',
    description: 'Đăng nhập hoặc đăng ký tài khoản AI Marketing Hub — quản lý SEO và marketing.',
    path: '/login',
  },
  adminusers: {
    title: 'Quản lý người dùng',
    description: 'Quản lý tài khoản người dùng — thay đổi vai trò, vô hiệu hóa tài khoản (admin).',
    path: '/admin/users',
  },
  seoworkspace: {
    title: 'SEO Workspace',
    description: 'Bộ công cụ SEO toàn diện — Technical SEO, CRO, Backlinks, Core Web Vitals, Link hỏng, Schema.',
    path: '/seo-workspace',
  },
  keywordhub: {
    title: 'Keyword Intelligence',
    description: 'Nghiên cứu từ khóa, phân tích đối thủ, SERP trực tiếp và theo dõi thứ hạng.',
    path: '/keyword-hub',
  },
  contentstudio: {
    title: 'Content Studio',
    description: 'Lập kế hoạch → Viết bài AI → Polish → Spin — workflow nội dung hoàn chỉnh.',
    path: '/content-studio',
  },
  schemageo: {
    title: 'Schema & GEO',
    description: 'Tạo và kiểm tra Schema.org markup cho Local SEO và Rich Snippets.',
    path: '/schema-geo',
  },
  aiadvisor: {
    title: 'AI Cố vấn website',
    description: 'AI Cố vấn tối ưu hóa website toàn diện — tổng hợp số liệu GSC, GA4, SEO Technical để đưa ra hành động có thứ tự ưu tiên.',
    path: '/ai-advisor',
  },
};

// Reverse lookup: URL path -> tab ID
const PATH_TO_TAB: Record<string, string> = {};
for (const [tabId, seo] of Object.entries(SEO_CONFIG)) {
  PATH_TO_TAB[seo.path] = tabId;
}

export function getTabIdFromPath(path: string): string {
  return PATH_TO_TAB[path] || 'dashboard';
}

// Get path from tab ID
export function getPathFromTabId(tabId: string): string {
  return SEO_CONFIG[tabId]?.path || '/';
}
