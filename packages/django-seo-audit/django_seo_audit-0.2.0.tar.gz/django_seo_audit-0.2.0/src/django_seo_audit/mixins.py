"""Django model mixins for SEO audit system.

This module contains reusable mixins that can be applied to Django models
to add SEO audit functionality without inheritance complexity.
"""

import json

from django.db.models.functions import Length


class SEOAuditableMixin:
    """Mixin implementing all SEO audit protocols for Django models.

    This mixin provides all the methods required by the SEO audit system's
    protocols (BasicSEOAuditable, SocialMediaAuditable, ContentAuditable,
    TechnicalSEOAuditable).

    Models using this mixin should have the appropriate SEO fields defined.
    """

    # BasicSEOAuditable Protocol Methods
    def get_seo_title(self) -> str:
        """Return SEO title with fallback to name or title."""
        return getattr(self, "seo_title", "") or getattr(self, "name", "") or getattr(self, "title", "")

    def get_meta_description(self) -> str:
        """Return meta description with fallback to short_description."""
        return getattr(self, "meta_description", "") or getattr(self, "short_description", "")

    def get_canonical_url(self) -> str:
        """Return canonical URL with fallback to absolute URL."""
        canonical = getattr(self, "canonical_url", "")
        if canonical:
            return canonical
        # Fallback to get_absolute_url if available
        if hasattr(self, "get_absolute_url"):
            return self.get_absolute_url()
        return ""

    def get_focus_keyphrase(self) -> str:
        """Return the primary keyword/phrase this object targets."""
        return getattr(self, "focus_keyphrase", "")

    def get_secondary_keywords(self) -> str:
        """Return comma-separated secondary keywords."""
        return getattr(self, "secondary_keywords", "")

    def get_h1_tag(self) -> str:
        """Return H1 tag with fallback to SEO title or name."""
        h1 = getattr(self, "h1_tag", "")
        return h1 or self.get_seo_title()

    # SocialMediaAuditable Protocol Methods
    def get_og_title(self) -> str:
        """Return OpenGraph title with fallback."""
        return getattr(self, "og_title", "") or self.get_seo_title()

    def get_og_description(self) -> str:
        """Return OpenGraph description with fallback."""
        return getattr(self, "og_description", "") or self.get_meta_description()

    def get_og_image_url(self) -> str | None:
        """Return the OpenGraph image URL, or None if not set."""
        og_image = getattr(self, "og_image", None)
        if not og_image:
            return None
        # Handle both ImageField (has .url) and URLField/CharField (is string)
        return og_image.url if hasattr(og_image, "url") else og_image

    def get_og_type(self) -> str:
        """Return the OpenGraph type (article, website, etc.)."""
        return getattr(self, "og_type", "") or "article"

    def get_twitter_title(self) -> str:
        """Return Twitter title with fallback."""
        return getattr(self, "twitter_title", "") or self.get_og_title()

    def get_twitter_description(self) -> str:
        """Return Twitter description with fallback."""
        return getattr(self, "twitter_description", "") or self.get_og_description()

    def get_twitter_image_url(self) -> str | None:
        """Return the Twitter Card image URL, or None if not set."""
        twitter_image = getattr(self, "twitter_image", None)
        if not twitter_image:
            return None
        # Handle both ImageField (has .url) and URLField/CharField (is string)
        return twitter_image.url if hasattr(twitter_image, "url") else twitter_image

    def get_twitter_card_type(self) -> str:
        """Return the Twitter Card type."""
        return getattr(self, "twitter_card_type", "") or "summary_large_image"

    # ContentAuditable Protocol Methods
    def has_detailed_content(self) -> bool:
        """Return True if object has detailed content beyond basic fields."""
        # Check if category has multiple published subpages with substantial content
        if hasattr(self, "subpages"):
            substantial_subpages = (
                self.subpages.filter(is_published=True)
                .exclude(content="")
                .annotate(content_length=Length("content"))
                .filter(
                    content_length__gte=500  # At least 500 characters of content
                )
            )
            minimum_substantial_subpages = 3
            return substantial_subpages.count() >= minimum_substantial_subpages
        return False

    def get_content_word_count(self) -> int:
        """Return the approximate word count of the main content."""
        # Count words in subpage content
        if hasattr(self, "subpages"):
            total_words = 0
            for subpage in self.subpages.filter(is_published=True):
                if subpage.content:
                    total_words += len(str(subpage.content).split())
            return total_words
        return 0

    def get_content_sections_count(self) -> int:
        """Return the number of content sections/chapters."""
        # Count published subpages as sections
        if hasattr(self, "subpages"):
            return self.subpages.filter(is_published=True).count()
        return 0

    def has_introduction_content(self) -> bool:
        """Return True if object has introduction content."""
        # Check if category has subpages with marketing cards generated
        if hasattr(self, "subpages"):
            subpages_with_cards = (
                self.subpages.filter(is_published=True).exclude(card_title="").exclude(card_title__isnull=True)
            )
            return subpages_with_cards.exists()  # At least one subpage has marketing cards
        return False

    def get_resource_count(self) -> int:
        """Return the number of associated resources (videos, articles, etc.)."""
        if hasattr(self, "resources"):
            return self.resources.count()
        return 0

    def get_featured_resource_count(self) -> int:
        """Return the number of featured/highlighted resources."""
        # Try to get through-model access for featured resources
        if hasattr(self, "categoryresource_set"):
            return self.categoryresource_set.filter(is_featured=True).count()
        return 0

    # TechnicalSEOAuditable Protocol Methods
    def get_robots_directive(self) -> str:
        """Return the robots meta directive (index,follow, etc.)."""
        return getattr(self, "robots_directive", "") or "index,follow"

    def get_schema_type(self) -> str:
        """Return the Schema.org type for structured data."""
        return getattr(self, "schema_type", "") or "Article"

    def get_schema_data(self) -> dict | None:
        """Return additional structured data as a dictionary."""
        schema_data = getattr(self, "schema_data", None)
        if not schema_data:
            return None

        if isinstance(schema_data, dict):
            return schema_data
        if isinstance(schema_data, str):
            try:
                return json.loads(schema_data)
            except (json.JSONDecodeError, TypeError):
                return None

        return None

    def get_breadcrumb_title(self) -> str:
        """Return breadcrumb title with fallback to name or title."""
        return getattr(self, "breadcrumb_title", "") or getattr(self, "name", "") or getattr(self, "title", "")

    def has_custom_canonical_url(self) -> bool:
        """Return True if a custom canonical URL is set."""
        canonical = getattr(self, "canonical_url", "")
        return bool(canonical and canonical.strip())

    # Utility Methods (used by existing helper methods)
    def get_structured_data(self) -> dict:
        """Return structured data for JSON-LD."""
        base_data = {
            "@context": "https://schema.org",
            "@type": self.get_schema_type(),
            "name": self.get_seo_title(),
            "description": self.get_meta_description(),
            "url": self.get_canonical_url(),
        }

        # Add additional schema data if provided
        additional_data = self.get_schema_data()
        if additional_data:
            base_data.update(additional_data)

        return base_data

    def get_structured_data_json(self) -> str:
        """Return structured data as JSON string for templates."""
        return json.dumps(self.get_structured_data())
