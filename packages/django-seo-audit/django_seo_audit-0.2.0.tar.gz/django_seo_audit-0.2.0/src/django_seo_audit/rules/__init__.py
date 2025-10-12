"""SEO audit rules - imported to trigger auto-registration."""

from . import (
    content_rules,  # noqa: F401
    core_seo_rules,  # noqa: F401
    social_media_rules,  # noqa: F401
    technical_seo_rules,  # noqa: F401
)

__all__ = ["content_rules", "core_seo_rules", "social_media_rules", "technical_seo_rules"]
