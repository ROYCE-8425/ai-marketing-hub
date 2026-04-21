"""
Pydantic schemas for /api/audit-seo and /api/audit-url endpoints
"""

from pydantic import BaseModel, Field, HttpUrl
from typing import Optional


class AuditSeoRequest(BaseModel):
    """Request schema for /api/audit-seo"""

    content: str = Field(
        ...,
        description="Full article content in plain text or Markdown",
        min_length=1,
    )
    meta_title: str = Field(
        ...,
        description="Meta title tag (50-60 characters recommended)",
    )
    primary_keyword: str = Field(
        ...,
        description="Primary target keyword for the article",
        min_length=1,
    )


class AuditUrlRequest(BaseModel):
    """Request schema for /api/audit-url (Phase 2)"""

    url: HttpUrl = Field(
        ...,
        description="Full URL of the page to scrape and analyze",
    )
    primary_keyword: str = Field(
        ...,
        description="Primary target keyword for SEO analysis",
        min_length=1,
    )
