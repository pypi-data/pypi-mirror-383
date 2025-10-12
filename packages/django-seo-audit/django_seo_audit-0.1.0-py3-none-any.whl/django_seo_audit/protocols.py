"""Protocol definitions for SEO auditable objects.

These protocols define the contracts that objects must implement to be audited
by different types of SEO rules. Using Python 3.12+ Protocol typing for clean
interface definition without inheritance requirements.
"""

from typing import Protocol


class BasicSEOAuditable(Protocol):
    """Basic contract for objects that can undergo core SEO auditing.

    This protocol defines the minimum interface required for fundamental
    SEO checks like title length, meta descriptions, and canonical URLs.
    """

    def get_seo_title(self) -> str:
        """Return the SEO-optimized title for this object."""
        ...

    def get_meta_description(self) -> str:
        """Return the meta description for this object."""
        ...

    def get_canonical_url(self) -> str:
        """Return the canonical URL for this object."""
        ...

    def get_focus_keyphrase(self) -> str:
        """Return the primary keyword/phrase this object targets."""
        ...

    def get_secondary_keywords(self) -> str:
        """Return comma-separated secondary keywords."""
        ...

    def get_h1_tag(self) -> str:
        """Return the H1 tag content for this object."""
        ...


class SocialMediaAuditable(Protocol):
    """Contract for objects that can undergo social media SEO auditing.

    This protocol defines the interface required for OpenGraph and
    Twitter Card optimization checks.
    """

    def get_og_title(self) -> str:
        """Return the OpenGraph title."""
        ...

    def get_og_description(self) -> str:
        """Return the OpenGraph description."""
        ...

    def get_og_image_url(self) -> str | None:
        """Return the OpenGraph image URL, or None if not set."""
        ...

    def get_og_type(self) -> str:
        """Return the OpenGraph type (article, website, etc.)."""
        ...

    def get_twitter_title(self) -> str:
        """Return the Twitter Card title."""
        ...

    def get_twitter_description(self) -> str:
        """Return the Twitter Card description."""
        ...

    def get_twitter_image_url(self) -> str | None:
        """Return the Twitter Card image URL, or None if not set."""
        ...

    def get_twitter_card_type(self) -> str:
        """Return the Twitter Card type."""
        ...


class ContentAuditable(Protocol):
    """Contract for objects that can undergo content-based SEO auditing.

    This protocol defines the interface required for content quality,
    structure, and completeness checks.
    """

    def has_detailed_content(self) -> bool:
        """Return True if object has detailed content beyond basic fields."""
        ...

    def get_content_word_count(self) -> int:
        """Return the approximate word count of the main content."""
        ...

    def get_content_sections_count(self) -> int:
        """Return the number of content sections/chapters."""
        ...

    def has_introduction_content(self) -> bool:
        """Return True if object has introduction content."""
        ...

    def get_resource_count(self) -> int:
        """Return the number of associated resources (videos, articles, etc.)."""
        ...

    def get_featured_resource_count(self) -> int:
        """Return the number of featured/highlighted resources."""
        ...


class TechnicalSEOAuditable(Protocol):
    """Contract for objects that can undergo technical SEO auditing.

    This protocol defines the interface required for technical SEO
    checks like robots directives, structured data, and performance.
    """

    def get_robots_directive(self) -> str:
        """Return the robots meta directive (index,follow, etc.)."""
        ...

    def get_schema_type(self) -> str:
        """Return the Schema.org type for structured data."""
        ...

    def get_schema_data(self) -> dict | None:
        """Return additional structured data as a dictionary."""
        ...

    def get_breadcrumb_title(self) -> str:
        """Return the breadcrumb navigation title."""
        ...

    def has_custom_canonical_url(self) -> bool:
        """Return True if a custom canonical URL is set."""
        ...


# Type alias for objects that support all SEO audit types
# Note: Individual protocols should be used in practice for specific rule requirements
class FullSEOAuditable(BasicSEOAuditable, SocialMediaAuditable, ContentAuditable, TechnicalSEOAuditable, Protocol):
    """Protocol for objects that support all SEO audit types."""
