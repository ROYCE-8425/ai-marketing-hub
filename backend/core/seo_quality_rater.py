"""
SEO Quality Rater

Rates content quality against SEO best practices and guidelines.
Provides scoring (0-100) and specific recommendations for improvement.
"""

import re
from typing import Dict, List, Optional, Any, Tuple


class SEOQualityRater:
    """Rates content against SEO best practices"""

    def __init__(self, guidelines: Optional[Dict[str, Any]] = None):
        """
        Initialize SEO Quality Rater

        Args:
            guidelines: Custom SEO guidelines (defaults to standard best practices)
        """
        self.guidelines = guidelines or self._default_guidelines()

    def _default_guidelines(self) -> Dict[str, Any]:
        """Default SEO guidelines based on industry standards"""
        return {
            'min_word_count': 2000,
            'optimal_word_count': 2500,
            'max_word_count': 3000,
            'primary_keyword_density_min': 1.0,
            'primary_keyword_density_max': 2.0,
            'secondary_keyword_density': 0.5,
            'min_internal_links': 3,
            'optimal_internal_links': 5,
            'min_external_links': 2,
            'optimal_external_links': 3,
            'meta_title_length_min': 50,
            'meta_title_length_max': 60,
            'meta_description_length_min': 150,
            'meta_description_length_max': 160,
            'min_h2_sections': 4,
            'optimal_h2_sections': 6,
            'h2_with_keyword_ratio': 0.33,  # At least 1/3 of H2s should have keyword
            'max_sentence_length': 25,
            'target_reading_level_min': 8,
            'target_reading_level_max': 10,
            'paragraph_sentence_min': 2,
            'paragraph_sentence_max': 4,
        }

    def rate(
        self,
        content: str,
        meta_title: Optional[str] = None,
        meta_description: Optional[str] = None,
        primary_keyword: Optional[str] = None,
        secondary_keywords: Optional[List[str]] = None,
        keyword_density: Optional[float] = None,
        internal_link_count: Optional[int] = None,
        external_link_count: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Rate content against SEO best practices

        Args:
            content: Article content
            meta_title: Meta title tag
            meta_description: Meta description tag
            primary_keyword: Target primary keyword
            secondary_keywords: Target secondary keywords
            keyword_density: Pre-calculated keyword density
            internal_link_count: Number of internal links
            external_link_count: Number of external links

        Returns:
            Dict with overall score, category scores, and recommendations
        """
        # Extract structure
        structure = self._analyze_structure(content, primary_keyword)

        # Score each category
        content_score = self._score_content(content, structure)
        keyword_score = self._score_keyword_optimization(
            content,
            structure,
            primary_keyword,
            secondary_keywords,
            keyword_density
        )
        meta_score = self._score_meta_elements(
            meta_title,
            meta_description,
            primary_keyword
        )
        structure_score = self._score_structure(structure)
        link_score = self._score_links(
            content,
            internal_link_count,
            external_link_count
        )
        readability_score = self._score_readability(content, structure)

        # Calculate overall score (weighted average)
        weights = {
            'content': 0.20,
            'keywords': 0.25,
            'meta': 0.15,
            'structure': 0.15,
            'links': 0.15,
            'readability': 0.10
        }

        overall_score = (
            content_score['score'] * weights['content'] +
            keyword_score['score'] * weights['keywords'] +
            meta_score['score'] * weights['meta'] +
            structure_score['score'] * weights['structure'] +
            link_score['score'] * weights['links'] +
            readability_score['score'] * weights['readability']
        )

        # Compile all issues
        critical_issues = []
        warnings = []
        suggestions = []

        for category in [content_score, keyword_score, meta_score, structure_score, link_score, readability_score]:
            critical_issues.extend(category.get('critical', []))
            warnings.extend(category.get('warnings', []))
            suggestions.extend(category.get('suggestions', []))

        return {
            'overall_score': round(overall_score, 1),
            'grade': self._get_grade(overall_score),
            'category_scores': {
                'content': content_score['score'],
                'keyword_optimization': keyword_score['score'],
                'meta_elements': meta_score['score'],
                'structure': structure_score['score'],
                'links': link_score['score'],
                'readability': readability_score['score']
            },
            'critical_issues': critical_issues,
            'warnings': warnings,
            'suggestions': suggestions,
            'publishing_ready': overall_score >= 80 and len(critical_issues) == 0,
            'details': {
                'word_count': structure['word_count'],
                'h2_count': structure['h2_count'],
                'has_h1': structure['has_h1'],
                'keyword_in_h1': structure.get('keyword_in_h1', False),
                'keyword_in_first_100': structure.get('keyword_in_first_100', False)
            }
        }

    def _analyze_structure(self, content: str, primary_keyword: Optional[str]) -> Dict[str, Any]:
        """Analyze content structure"""
        lines = content.split('\n')

        # Extract headings
        h1_count = 0
        h2_count = 0
        h3_count = 0
        h1_text = ""
        h2_texts = []
        h3_texts = []

        for line in lines:
            h1_match = re.match(r'^#\s+(.+)$', line)
            h2_match = re.match(r'^##\s+(.+)$', line)
            h3_match = re.match(r'^###\s+(.+)$', line)

            if h1_match:
                h1_count += 1
                if not h1_text:  # First H1
                    h1_text = h1_match.group(1)
            elif h2_match:
                h2_count += 1
                h2_texts.append(h2_match.group(1))
            elif h3_match:
                h3_count += 1
                h3_texts.append(h3_match.group(1))

        # Word count
        word_count = len(content.split())

        # Paragraph analysis
        paragraphs = [p for p in content.split('\n\n') if p.strip() and not p.strip().startswith('#')]
        avg_paragraph_length = sum(len(p.split()) for p in paragraphs) / len(paragraphs) if paragraphs else 0

        # Keyword checks
        keyword_in_h1 = False
        keyword_in_first_100 = False
        h2_with_keyword = 0

        if primary_keyword:
            keyword_lower = primary_keyword.lower()
            keyword_in_h1 = keyword_lower in h1_text.lower()
            first_100_words = ' '.join(content.split()[:100]).lower()
            keyword_in_first_100 = keyword_lower in first_100_words

            for h2 in h2_texts:
                if keyword_lower in h2.lower():
                    h2_with_keyword += 1

        return {
            'word_count': word_count,
            'has_h1': h1_count > 0,
            'h1_count': h1_count,
            'h1_text': h1_text,
            'h2_count': h2_count,
            'h2_texts': h2_texts,
            'h3_count': h3_count,
            'paragraph_count': len(paragraphs),
            'avg_paragraph_length': avg_paragraph_length,
            'keyword_in_h1': keyword_in_h1,
            'keyword_in_first_100': keyword_in_first_100,
            'h2_with_keyword': h2_with_keyword
        }

    def _score_content(self, content: str, structure: Dict) -> Dict[str, Any]:
        """Score content length and quality"""
        score = 100
        critical = []
        warnings = []
        suggestions = []

        word_count = structure['word_count']
        min_words = self.guidelines['min_word_count']
        optimal_words = self.guidelines['optimal_word_count']
        max_words = self.guidelines['max_word_count']

        # Word count scoring
        if word_count < min_words:
            score -= 30
            critical.append(f"Nội dung quá ngắn ({word_count} từ). Tối thiểu cần {min_words} từ.")
        elif word_count < optimal_words:
            score -= 10
            warnings.append(f"Nội dung nên dài hơn ({word_count} từ). Khuyến nghị {optimal_words}+ từ.")
        elif word_count > max_words:
            score -= 5
            suggestions.append(f"Nội dung khá dài ({word_count} từ). Nên tách thành nhiều bài nếu vượt {max_words} từ.")

        # Paragraph length
        avg_para = structure['avg_paragraph_length']
        if avg_para > 150:
            score -= 10
            warnings.append(f"Đoạn văn quá dài (trung bình {avg_para:.0f} từ). Nên chia thành đoạn 2-4 câu.")
        elif avg_para < 30:
            score -= 5
            suggestions.append(f"Đoạn văn quá ngắn (trung bình {avg_para:.0f} từ). Nên bổ sung thêm chi tiết.")

        return {
            'score': max(0, score),
            'critical': critical,
            'warnings': warnings,
            'suggestions': suggestions
        }

    def _score_keyword_optimization(
        self,
        content: str,
        structure: Dict,
        primary_keyword: Optional[str],
        secondary_keywords: Optional[List[str]],
        keyword_density: Optional[float]
    ) -> Dict[str, Any]:
        """Score keyword optimization"""
        score = 100
        critical = []
        warnings = []
        suggestions = []

        if not primary_keyword:
            return {
                'score': 50,
                'critical': ['Chưa chỉ định từ khóa chính'],
                'warnings': [],
                'suggestions': []
            }

        # Keyword in H1
        if not structure['keyword_in_h1']:
            score -= 20
            critical.append(f"Từ khóa chính \"{primary_keyword}\" chưa xuất hiện trong H1")

        # Keyword in first 100 words
        if not structure['keyword_in_first_100']:
            score -= 15
            critical.append(f"Từ khóa chính \"{primary_keyword}\" chưa xuất hiện trong 100 từ đầu tiên")

        # Keyword in H2 headings
        h2_count = structure['h2_count']
        h2_with_kw = structure['h2_with_keyword']
        if h2_count > 0:
            ratio = h2_with_kw / h2_count
            target_ratio = self.guidelines['h2_with_keyword_ratio']
            if ratio < target_ratio:
                score -= 10
                warnings.append(
                    f"Từ khóa chỉ xuất hiện trong {h2_with_kw}/{h2_count} tiêu đề H2. "
                    f"Nên đạt ít nhất {int(target_ratio * 100)}% (2-3 H2)"
                )

        # Keyword density
        if keyword_density is not None:
            min_density = self.guidelines['primary_keyword_density_min']
            max_density = self.guidelines['primary_keyword_density_max']

            if keyword_density < min_density:
                score -= 15
                warnings.append(
                    f"Keyword density quá thấp ({keyword_density}%). "
                    f"Nên đạt {min_density}-{max_density}%"
                )
            elif keyword_density > max_density * 1.5:
                score -= 20
                critical.append(
                    f"Keyword density quá cao ({keyword_density}%). "
                    f"Có nguy cơ nhồi từ khóa. Nên đạt {min_density}-{max_density}%"
                )
            elif keyword_density > max_density:
                score -= 10
                warnings.append(
                    f"Keyword density hơi cao ({keyword_density}%). "
                    f"Nên đạt {min_density}-{max_density}%"
                )

        # Secondary keywords
        if secondary_keywords:
            content_lower = content.lower()
            missing_keywords = [kw for kw in secondary_keywords if kw.lower() not in content_lower]
            if missing_keywords:
                score -= 5
                suggestions.append(f"Thiếu từ khóa phụ: {', '.join(missing_keywords)}")

        return {
            'score': max(0, score),
            'critical': critical,
            'warnings': warnings,
            'suggestions': suggestions
        }

    def _score_meta_elements(
        self,
        meta_title: Optional[str],
        meta_description: Optional[str],
        primary_keyword: Optional[str]
    ) -> Dict[str, Any]:
        """Score meta title and description"""
        score = 100
        critical = []
        warnings = []
        suggestions = []

        # Meta title
        if not meta_title:
            score -= 40
            critical.append("Thiếu meta title")
        else:
            title_len = len(meta_title)
            min_len = self.guidelines['meta_title_length_min']
            max_len = self.guidelines['meta_title_length_max']

            if title_len < min_len:
                score -= 15
                warnings.append(f"Meta title quá ngắn ({title_len} ký tự). Nên đạt {min_len}-{max_len} ký tự.")
            elif title_len > max_len + 10:
                score -= 10
                warnings.append(f"Meta title quá dài ({title_len} ký tự). Nên đạt {min_len}-{max_len} ký tự.")

            if primary_keyword and primary_keyword.lower() not in meta_title.lower():
                score -= 15
                warnings.append(f"Từ khóa chính \"{primary_keyword}\" chưa có trong meta title")

        # Meta description
        if not meta_description:
            score -= 40
            critical.append("Thiếu meta description")
        else:
            desc_len = len(meta_description)
            min_len = self.guidelines['meta_description_length_min']
            max_len = self.guidelines['meta_description_length_max']

            if desc_len < min_len:
                score -= 15
                warnings.append(f"Meta description quá ngắn ({desc_len} ký tự). Nên đạt {min_len}-{max_len} ký tự.")
            elif desc_len > max_len + 10:
                score -= 10
                warnings.append(f"Meta description quá dài ({desc_len} ký tự). Nên đạt {min_len}-{max_len} ký tự.")

            if primary_keyword and primary_keyword.lower() not in meta_description.lower():
                score -= 10
                suggestions.append(f"Từ khóa chính \"{primary_keyword}\" chưa có trong meta description")

        return {
            'score': max(0, score),
            'critical': critical,
            'warnings': warnings,
            'suggestions': suggestions
        }

    def _score_structure(self, structure: Dict) -> Dict[str, Any]:
        """Score content structure"""
        score = 100
        critical = []
        warnings = []
        suggestions = []

        # H1 check
        if not structure['has_h1']:
            score -= 30
            critical.append("Thiếu tiêu đề H1")
        elif structure['h1_count'] > 1:
            score -= 20
            critical.append(f"Có nhiều H1 ({structure['h1_count']}). Chỉ nên có duy nhất 1 H1.")

        # H2 count
        h2_count = structure['h2_count']
        min_h2 = self.guidelines['min_h2_sections']
        optimal_h2 = self.guidelines['optimal_h2_sections']

        if h2_count < min_h2:
            score -= 15
            warnings.append(f"Quá ít mục H2 ({h2_count}). Nên bổ sung thêm (khuyến nghị: {optimal_h2}).")
        elif h2_count < optimal_h2:
            score -= 5
            suggestions.append(f"Nên thêm mục H2 ({h2_count} hiện tại). Khuyến nghị {optimal_h2} mục.")

        return {
            'score': max(0, score),
            'critical': critical,
            'warnings': warnings,
            'suggestions': suggestions
        }

    def _score_links(
        self,
        content: str,
        internal_count: Optional[int],
        external_count: Optional[int]
    ) -> Dict[str, Any]:
        """Score internal and external linking"""
        score = 100
        critical = []
        warnings = []
        suggestions = []

        # Count links if not provided
        if internal_count is None:
            internal_count = len(re.findall(r'\[([^\]]+)\]\((?!http)', content))

        if external_count is None:
            external_count = len(re.findall(r'\[([^\]]+)\]\(https?://', content))

        # Internal links
        min_internal = self.guidelines['min_internal_links']
        optimal_internal = self.guidelines['optimal_internal_links']

        if internal_count < min_internal:
            score -= 20
            warnings.append(
                f"Internal links quá ít (hiện tại: {internal_count}). "
                f"Nên bổ sung thêm {min_internal - internal_count} liên kết nội bộ (khuyến nghị: {optimal_internal})."
            )
        elif internal_count < optimal_internal:
            score -= 5
            suggestions.append(f"Nên thêm internal links ({internal_count} hiện tại). Khuyến nghị {optimal_internal}.")

        # External links
        min_external = self.guidelines['min_external_links']
        optimal_external = self.guidelines['optimal_external_links']

        if external_count < min_external:
            score -= 15
            warnings.append(
                f"External links quá ít (hiện tại: {external_count}). "
                f"Nên bổ sung nguồn uy tín (khuyến nghị: {optimal_external})."
            )
        elif external_count < optimal_external:
            score -= 5
            suggestions.append(f"Nên thêm external links ({external_count} hiện tại). Khuyến nghị {optimal_external}.")

        return {
            'score': max(0, score),
            'critical': critical,
            'warnings': warnings,
            'suggestions': suggestions
        }

    def _score_readability(self, content: str, structure: Dict) -> Dict[str, Any]:
        """Score readability factors"""
        score = 100
        critical = []
        warnings = []
        suggestions = []

        # Sentence length analysis
        sentences = re.split(r'[.!?]+', content)
        sentences = [s.strip() for s in sentences if s.strip()]

        sentence_lengths = [len(s.split()) for s in sentences]
        avg_sentence_length = sum(sentence_lengths) / len(sentence_lengths) if sentence_lengths else 0

        max_sentence = self.guidelines['max_sentence_length']
        if avg_sentence_length > max_sentence:
            score -= 10
            warnings.append(
                f"Câu trung bình dài {avg_sentence_length:.1f} từ. "
                f"Nên dưới {max_sentence} từ để dễ đọc hơn."
            )

        # Very long sentences
        long_sentences = [s for s in sentence_lengths if s > max_sentence * 1.5]
        if len(long_sentences) > len(sentences) * 0.2:  # More than 20% are too long
            score -= 10
            warnings.append(
                f"{len(long_sentences)} câu quá dài (>{max_sentence * 1.5} từ). "
                "Nên tách thành các câu ngắn hơn."
            )

        # Lists and formatting
        bullet_lists = len(re.findall(r'^\s*[-*+]\s', content, re.MULTILINE))
        numbered_lists = len(re.findall(r'^\s*\d+\.\s', content, re.MULTILINE))

        if bullet_lists + numbered_lists == 0:
            score -= 5
            suggestions.append("Chưa có danh sách (bullet/numbered list). Nên sử dụng để tăng khả năng quét nội dung.")

        return {
            'score': max(0, score),
            'critical': critical,
            'warnings': warnings,
            'suggestions': suggestions
        }

    def _get_grade(self, score: float) -> str:
        """Convert score to letter grade"""
        if score >= 90:
            return "A (Xuất sắc)"
        elif score >= 80:
            return "B (Tốt)"
        elif score >= 70:
            return "C (Trung bình)"
        elif score >= 60:
            return "D (Cần cải thiện)"
        else:
            return "F (Yếu)"


# ── Page-type-aware SEO scorer (DOM-based) ───────────────────────────────────

# Guidelines vary by page type — a homepage doesn't need 2000 words
GUIDELINES_BY_PAGE_TYPE: Dict[str, Dict[str, Any]] = {
    "homepage": {
        "min_word_count": 150, "optimal_word_count": 500,
        "min_h2": 1, "optimal_h2": 3,
        "min_internal_links": 5, "min_external_links": 0,
        "meta_title_min": 30, "meta_title_max": 65,
        "meta_desc_min": 80, "meta_desc_max": 165,
    },
    "article": {
        "min_word_count": 1200, "optimal_word_count": 2500,
        "min_h2": 3, "optimal_h2": 6,
        "min_internal_links": 3, "min_external_links": 1,
        "meta_title_min": 40, "meta_title_max": 65,
        "meta_desc_min": 120, "meta_desc_max": 165,
    },
    "product": {
        "min_word_count": 200, "optimal_word_count": 800,
        "min_h2": 1, "optimal_h2": 4,
        "min_internal_links": 2, "min_external_links": 0,
        "meta_title_min": 30, "meta_title_max": 65,
        "meta_desc_min": 80, "meta_desc_max": 165,
    },
    "service": {
        "min_word_count": 400, "optimal_word_count": 1200,
        "min_h2": 2, "optimal_h2": 5,
        "min_internal_links": 3, "min_external_links": 1,
        "meta_title_min": 35, "meta_title_max": 65,
        "meta_desc_min": 100, "meta_desc_max": 165,
    },
    "listing": {
        "min_word_count": 50, "optimal_word_count": 300,
        "min_h2": 0, "optimal_h2": 2,
        "min_internal_links": 5, "min_external_links": 0,
        "meta_title_min": 30, "meta_title_max": 65,
        "meta_desc_min": 80, "meta_desc_max": 165,
    },
    "other": {
        "min_word_count": 300, "optimal_word_count": 1000,
        "min_h2": 2, "optimal_h2": 4,
        "min_internal_links": 2, "min_external_links": 1,
        "meta_title_min": 35, "meta_title_max": 65,
        "meta_desc_min": 100, "meta_desc_max": 165,
    },
}


def _grade(score: float) -> str:
    """Convert numeric score to Vietnamese letter grade."""
    if score >= 90: return "A (Xuất sắc)"
    if score >= 80: return "B (Tốt)"
    if score >= 70: return "C (Trung bình)"
    if score >= 60: return "D (Cần cải thiện)"
    return "F (Yếu)"


def rate_page_seo(
    features: Any,  # PageFeatures from html_page_parser
    primary_keyword: str = "",
) -> Dict[str, Any]:
    """
    Score a live page using DOM-measured PageFeatures.

    8 categories, 100 total points.
    Each category is labeled as 'measured' or 'rule_based'.

    Args:
        features: PageFeatures instance from html_page_parser
        primary_keyword: Target keyword for on-page analysis

    Returns:
        Dict with score, grade, breakdown, issues, and data_sources
    """
    g = GUIDELINES_BY_PAGE_TYPE.get(features.page_type, GUIDELINES_BY_PAGE_TYPE["other"])

    critical_issues: List[str] = []
    warnings: List[str] = []
    suggestions: List[str] = []

    # ── 1. Indexability & Crawlability (20 pts) ── type: measured ─────────
    idx_score = 20
    idx_details: Dict[str, Any] = {}

    if features.has_noindex:
        idx_score -= 20
        critical_issues.append("Trang có meta robots noindex — Google sẽ KHÔNG index trang này")
    idx_details["has_noindex"] = features.has_noindex

    if not features.canonical_url:
        idx_score -= 5
        warnings.append("Thiếu canonical URL — có thể gây duplicate content")
    idx_details["canonical_url"] = features.canonical_url

    if not features.is_https:
        idx_score -= 5
        critical_issues.append("Trang không dùng HTTPS — Google ưu tiên HTTPS")
    idx_details["is_https"] = features.is_https

    idx_score = max(0, idx_score)

    # ── 2. Metadata (15 pts) ── type: rule_based ─────────────────────────
    meta_score = 15
    meta_details: Dict[str, Any] = {}

    if not features.meta_title:
        meta_score -= 8
        critical_issues.append("Thiếu thẻ <title>")
    else:
        if features.meta_title_length < g["meta_title_min"]:
            meta_score -= 3
            warnings.append(f"Title quá ngắn ({features.meta_title_length} ký tự). Nên {g['meta_title_min']}-{g['meta_title_max']} ký tự.")
        elif features.meta_title_length > g["meta_title_max"] + 10:
            meta_score -= 2
            warnings.append(f"Title quá dài ({features.meta_title_length} ký tự). Nên dưới {g['meta_title_max']} ký tự.")

        if primary_keyword and primary_keyword.lower() not in features.meta_title.lower():
            meta_score -= 3
            warnings.append(f'Từ khóa chính "{primary_keyword}" chưa có trong title')

    meta_details["title"] = features.meta_title
    meta_details["title_length"] = features.meta_title_length

    if not features.meta_description:
        meta_score -= 5
        critical_issues.append("Thiếu meta description")
    else:
        if features.meta_description_length < g["meta_desc_min"]:
            meta_score -= 2
            warnings.append(f"Meta description quá ngắn ({features.meta_description_length} ký tự). Nên {g['meta_desc_min']}-{g['meta_desc_max']} ký tự.")
        elif features.meta_description_length > g["meta_desc_max"] + 10:
            meta_score -= 1
            warnings.append(f"Meta description quá dài ({features.meta_description_length} ký tự). Nên dưới {g['meta_desc_max']} ký tự.")

        if primary_keyword and primary_keyword.lower() not in features.meta_description.lower():
            meta_score -= 1
            suggestions.append(f'Từ khóa chính "{primary_keyword}" chưa có trong meta description')

    meta_details["description"] = features.meta_description[:100]
    meta_details["description_length"] = features.meta_description_length

    meta_score = max(0, meta_score)

    # ── 3. Heading & Content Structure (15 pts) ── type: measured ────────
    heading_score = 15
    heading_details: Dict[str, Any] = {}

    if features.h1_count == 0:
        heading_score -= 8
        critical_issues.append("Thiếu thẻ H1")
    elif features.h1_count > 1:
        heading_score -= 4
        warnings.append(f"Có {features.h1_count} thẻ H1 (nên chỉ có 1)")

    heading_details["h1_count"] = features.h1_count
    heading_details["h1_texts"] = features.h1_texts[:3]

    if features.h2_count < g["min_h2"]:
        heading_score -= 4
        warnings.append(f"Quá ít H2 ({features.h2_count}). Nên có ít nhất {g['min_h2']}.")
    elif features.h2_count < g["optimal_h2"]:
        heading_score -= 1
        suggestions.append(f"Nên thêm H2 ({features.h2_count} hiện tại). Khuyến nghị {g['optimal_h2']}.")

    heading_details["h2_count"] = features.h2_count
    heading_details["h3_count"] = features.h3_count

    heading_score = max(0, heading_score)

    # ── 4. Content Quality On-page (15 pts) ── type: rule_based ──────────
    content_score = 15
    content_details: Dict[str, Any] = {}

    if features.word_count < g["min_word_count"]:
        content_score -= 8
        critical_issues.append(f"Nội dung quá ngắn ({features.word_count} từ). Tối thiểu {g['min_word_count']} từ cho {features.page_type} page.")
    elif features.word_count < g["optimal_word_count"]:
        content_score -= 3
        suggestions.append(f"Nội dung nên dài hơn ({features.word_count} từ). Khuyến nghị {g['optimal_word_count']}+ cho {features.page_type} page.")

    content_details["word_count"] = features.word_count
    content_details["paragraph_count"] = features.paragraph_count
    content_details["has_lists"] = features.has_lists
    content_details["has_tables"] = features.has_tables

    if not features.has_lists and features.page_type in ("article", "service", "product"):
        content_score -= 2
        suggestions.append("Chưa có danh sách (bullet/numbered). Nên sử dụng để cải thiện khả năng đọc.")

    content_score = max(0, content_score)

    # ── 5. Keyword Targeting (10 pts) ── type: rule_based ────────────────
    kw_score = 10
    kw_details: Dict[str, Any] = {}

    if not primary_keyword:
        kw_score = 5  # Neutral if no keyword provided
        kw_details["note"] = "Chưa chỉ định từ khóa chính"
    else:
        kw_lower = primary_keyword.lower()

        # Keyword in H1
        kw_in_h1 = any(kw_lower in h.lower() for h in features.h1_texts)
        if not kw_in_h1 and features.h1_count > 0:
            kw_score -= 3
            warnings.append(f'Từ khóa "{primary_keyword}" chưa xuất hiện trong H1')
        kw_details["in_h1"] = kw_in_h1

        # Keyword in first 100 words
        first_100 = " ".join(features.visible_text.split()[:100]).lower()
        kw_in_first_100 = kw_lower in first_100
        if not kw_in_first_100:
            kw_score -= 3
            warnings.append(f'Từ khóa "{primary_keyword}" chưa xuất hiện trong 100 từ đầu')
        kw_details["in_first_100_words"] = kw_in_first_100

        # Keyword in H2 (secondary signal)
        h2_with_kw = sum(1 for h in features.h2_texts if kw_lower in h.lower())
        if features.h2_count > 0 and h2_with_kw == 0:
            kw_score -= 2
            suggestions.append(f'Nên thêm từ khóa "{primary_keyword}" vào 1-2 tiêu đề H2')
        kw_details["in_h2_count"] = h2_with_kw
        kw_details["h2_total"] = features.h2_count

        # Density (secondary signal, light weight)
        if features.word_count > 0:
            kw_count = features.visible_text.lower().count(kw_lower)
            density = round(kw_count / features.word_count * 100, 2)
            kw_details["density"] = density
            kw_details["occurrences"] = kw_count
            if density > 3.0:
                kw_score -= 2
                warnings.append(f"Keyword density quá cao ({density}%). Có nguy cơ nhồi từ khóa.")
        else:
            kw_details["density"] = 0

    kw_score = max(0, kw_score)

    # ── 6. Internal/External Linking (10 pts) ── type: measured ──────────
    link_score = 10
    link_details: Dict[str, Any] = {}

    if features.internal_links < g["min_internal_links"]:
        link_score -= 5
        warnings.append(f"Internal links ít ({features.internal_links}). Nên có ít nhất {g['min_internal_links']}.")

    if features.page_type in ("article", "service", "other"):
        if features.external_links < g["min_external_links"]:
            link_score -= 3
            suggestions.append(f"Nên thêm external links đến nguồn uy tín ({features.external_links} hiện tại).")

    link_details["internal"] = features.internal_links
    link_details["external"] = features.external_links
    link_details["nofollow"] = features.nofollow_links

    link_score = max(0, link_score)

    # ── 7. Media & Accessibility (5 pts) ── type: measured ───────────────
    media_score = 5
    media_details: Dict[str, Any] = {}

    if features.images_total > 0:
        alt_ratio = features.images_with_alt / features.images_total
        if alt_ratio < 0.5:
            media_score -= 3
            warnings.append(f"{features.images_missing_alt}/{features.images_total} hình thiếu alt text")
        elif alt_ratio < 0.8:
            media_score -= 1
            suggestions.append(f"{features.images_missing_alt} hình thiếu alt text")
    elif features.page_type in ("article", "product"):
        media_score -= 2
        suggestions.append("Nên thêm hình ảnh minh họa")

    media_details["images_total"] = features.images_total
    media_details["images_with_alt"] = features.images_with_alt
    media_details["has_video"] = features.has_video

    media_score = max(0, media_score)

    # ── 8. Technical UX Signals (10 pts) ── type: measured ───────────────
    tech_score = 10
    tech_details: Dict[str, Any] = {}

    if not features.has_viewport:
        tech_score -= 5
        critical_issues.append("Thiếu meta viewport — trang không responsive")
    tech_details["has_viewport"] = features.has_viewport

    if not features.lang_attribute:
        tech_score -= 2
        suggestions.append("Thiếu thuộc tính lang trên <html> — ảnh hưởng accessibility")
    tech_details["lang"] = features.lang_attribute

    og_count = len(features.og_tags)
    if og_count < 3:
        tech_score -= 2
        suggestions.append(f"Thiếu Open Graph tags ({og_count}/3). Ảnh hưởng chia sẻ mạng xã hội.")
    tech_details["og_tags_count"] = og_count

    tech_score = max(0, tech_score)

    # ── Overall ──────────────────────────────────────────────────────────
    overall = idx_score + meta_score + heading_score + content_score + kw_score + link_score + media_score + tech_score

    return {
        "overall_score": round(overall, 1),
        "grade": _grade(overall),
        "page_type": features.page_type,
        "page_type_confidence": features.page_type_confidence,
        "confidence": "high" if features.page_type_confidence != "low" else "medium",
        "publishing_ready": overall >= 75 and len(critical_issues) == 0,
        "category_scores": {
            "indexability": idx_score,
            "metadata": meta_score,
            "headings_structure": heading_score,
            "content_quality": content_score,
            "keyword_targeting": kw_score,
            "linking": link_score,
            "media_accessibility": media_score,
            "technical_ux": tech_score,
        },
        "category_max": {
            "indexability": 20,
            "metadata": 15,
            "headings_structure": 15,
            "content_quality": 15,
            "keyword_targeting": 10,
            "linking": 10,
            "media_accessibility": 5,
            "technical_ux": 10,
        },
        "data_sources": {
            "indexability": "measured",
            "metadata": "rule_based",
            "headings_structure": "measured",
            "content_quality": "rule_based",
            "keyword_targeting": "rule_based",
            "linking": "measured",
            "media_accessibility": "measured",
            "technical_ux": "measured",
        },
        "critical_issues": critical_issues,
        "warnings": warnings,
        "suggestions": suggestions,
        "details": {
            "indexability": idx_details,
            "metadata": meta_details,
            "headings": heading_details,
            "content": content_details,
            "keyword": kw_details,
            "links": link_details,
            "media": media_details,
            "technical": tech_details,
        },
    }


# ── Legacy convenience function (kept for audit-seo raw text endpoint) ───────
def rate_seo_quality(
    content: str,
    meta_title: Optional[str] = None,
    meta_description: Optional[str] = None,
    primary_keyword: Optional[str] = None,
    secondary_keywords: Optional[List[str]] = None,
    keyword_density: Optional[float] = None,
    internal_link_count: Optional[int] = None,
    external_link_count: Optional[int] = None,
    custom_guidelines: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Rate SEO quality of raw text content (for pre-publish article audit).

    This is the LEGACY function for audit-seo endpoint.
    For live page scoring, use rate_page_seo() with PageFeatures instead.
    """
    rater = SEOQualityRater(custom_guidelines)
    return rater.rate(
        content,
        meta_title,
        meta_description,
        primary_keyword,
        secondary_keywords,
        keyword_density,
        internal_link_count,
        external_link_count
    )

