// JSON-LD structured data schema builders for SEO

export function buildOrganizationSchema() {
  return {
    '@context': 'https://schema.org',
    '@type': 'Organization',
    name: 'AI Marketing Hub',
    url: 'https://binhphuocmitsubishi.com',
    logo: 'https://binhphuocmitsubishi.com/favicon.svg',
    description: 'Nền tảng AI Marketing & SEO tự động hóa cho thị trường Việt Nam',
    founder: { '@type': 'Person', name: 'Trần Như Ý' },
  };
}

export function buildWebSiteSchema() {
  return {
    '@context': 'https://schema.org',
    '@type': 'WebSite',
    name: 'AI Marketing Hub',
    url: 'https://binhphuocmitsubishi.com',
    potentialAction: {
      '@type': 'SearchAction',
      target: 'https://binhphuocmitsubishi.com/search?q={search_term_string}',
      'query-input': 'required name=search_term_string',
    },
  };
}

export function buildSoftwareAppSchema() {
  return {
    '@context': 'https://schema.org',
    '@type': 'SoftwareApplication',
    name: 'AI Marketing Hub',
    applicationCategory: 'BusinessApplication',
    operatingSystem: 'Web',
    offers: { '@type': 'Offer', price: '0', priceCurrency: 'VND' },
    description: 'Nền tảng tối ưu SEO & Marketing bằng AI cho thị trường Việt Nam',
  };
}

export function buildBreadcrumbSchema(items: { name: string; url: string }[]) {
  return {
    '@context': 'https://schema.org',
    '@type': 'BreadcrumbList',
    itemListElement: items.map((item, index) => ({
      '@type': 'ListItem',
      position: index + 1,
      name: item.name,
      item: item.url,
    })),
  };
}
