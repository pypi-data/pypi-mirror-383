"""Django SEO Audit - Protocol-based SEO auditing framework for Django models.

A clean, extensible system for auditing Django models against SEO best practices.
Uses Python protocols for loose coupling and automatic rule discovery.
"""

from .core import SEOResult, SEORule, SEOStatus
from .mixins import SEOAuditableMixin
from .protocols import BasicSEOAuditable, ContentAuditable, SocialMediaAuditable, TechnicalSEOAuditable
from .registry import SEOAuditor, SEOAuditResult, SEORuleRegistry

__version__ = "0.1.0"

__all__ = [
    "BasicSEOAuditable",
    "ContentAuditable",
    "SEOAuditableMixin",
    "SEOAuditor",
    "SEOAuditResult",
    "SEOResult",
    "SEORule",
    "SEORuleRegistry",
    "SEOStatus",
    "SocialMediaAuditable",
    "TechnicalSEOAuditable",
]
