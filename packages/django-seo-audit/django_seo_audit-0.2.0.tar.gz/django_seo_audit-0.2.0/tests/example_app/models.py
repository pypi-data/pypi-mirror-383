"""Example models demonstrating django-seo-audit usage patterns."""

from django.db import models

from django_seo_audit import SEOAuditableMixin


class BlogPost(SEOAuditableMixin, models.Model):
    """Full-featured blog post with all SEO fields.

    This model demonstrates complete SEO optimization with all available fields.
    Use this as a reference for comprehensive SEO implementation.
    """

    # Basic fields
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    content = models.TextField()
    excerpt = models.TextField(max_length=300, blank=True)

    # Core SEO fields
    seo_title = models.CharField(max_length=60, blank=True, help_text="Optimal: 50-60 characters")
    meta_description = models.CharField(max_length=160, blank=True, help_text="Optimal: 150-160 characters")
    h1_tag = models.CharField(max_length=100, blank=True, help_text="Main heading tag")
    focus_keyphrase = models.CharField(max_length=100, blank=True, help_text="Primary keyword to target")
    secondary_keywords = models.CharField(max_length=255, blank=True, help_text="Comma-separated keywords")
    canonical_url = models.URLField(blank=True, help_text="Canonical URL for this content")

    # Social media fields
    og_title = models.CharField(max_length=95, blank=True, help_text="OpenGraph title (up to 95 chars)")
    og_description = models.CharField(max_length=200, blank=True, help_text="OpenGraph description")
    og_image = models.URLField(blank=True, help_text="OpenGraph image URL")
    og_type = models.CharField(max_length=20, default="article")

    twitter_title = models.CharField(max_length=70, blank=True, help_text="Twitter Card title")
    twitter_description = models.CharField(max_length=200, blank=True, help_text="Twitter Card description")
    twitter_image = models.URLField(blank=True, help_text="Twitter Card image URL")
    twitter_card_type = models.CharField(max_length=20, default="summary_large_image")

    # Technical SEO fields
    robots_directive = models.CharField(max_length=50, default="index,follow")
    schema_type = models.CharField(max_length=50, default="BlogPosting")
    schema_data = models.JSONField(blank=True, null=True, help_text="Additional structured data")
    breadcrumb_title = models.CharField(max_length=100, blank=True)

    # Publishing metadata
    is_published = models.BooleanField(default=False)
    published_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Blog Post"
        verbose_name_plural = "Blog Posts"

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        """Return the absolute URL for this blog post."""
        return f"/blog/{self.slug}/"


class Product(SEOAuditableMixin, models.Model):
    """Minimal product model demonstrating fallback behavior.

    This model shows how django-seo-audit works with minimal SEO fields,
    relying on intelligent fallbacks from the mixin.
    """

    # Basic fields (mixin will fall back to these)
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    short_description = models.CharField(max_length=200, blank=True)

    # Minimal SEO fields (most will use fallbacks)
    seo_title = models.CharField(max_length=60, blank=True)
    meta_description = models.CharField(max_length=160, blank=True)

    # Product-specific fields
    price = models.DecimalField(max_digits=10, decimal_places=2)
    sku = models.CharField(max_length=50, unique=True)
    in_stock = models.BooleanField(default=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Product"
        verbose_name_plural = "Products"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        """Return the absolute URL for this product."""
        return f"/products/{self.slug}/"


class Page(models.Model):
    """Custom page model implementing protocols without using the mixin.

    This model demonstrates how to implement SEO audit protocols manually
    without inheriting from SEOAuditableMixin. Useful when you need full
    control over the implementation or have existing models.
    """

    # Basic fields
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    content = models.TextField()

    # SEO fields
    page_title = models.CharField(max_length=60, blank=True, help_text="Browser tab title")
    meta_desc = models.CharField(max_length=160, blank=True, help_text="Meta description")
    primary_keyword = models.CharField(max_length=100, blank=True)

    # Page metadata
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["title"]
        verbose_name = "Page"
        verbose_name_plural = "Pages"

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        """Return the absolute URL for this page."""
        return f"/pages/{self.slug}/"

    # Implement BasicSEOAuditable protocol methods manually
    def get_seo_title(self) -> str:
        """Return SEO title with fallback to page title."""
        return self.page_title or self.title

    def get_meta_description(self) -> str:
        """Return meta description."""
        return self.meta_desc

    def get_canonical_url(self) -> str:
        """Return canonical URL."""
        return self.get_absolute_url()

    def get_focus_keyphrase(self) -> str:
        """Return primary keyword."""
        return self.primary_keyword

    def get_secondary_keywords(self) -> str:
        """Return empty string (no secondary keywords on this model)."""
        return ""

    def get_h1_tag(self) -> str:
        """Return H1 tag with fallback to title."""
        return self.title

    # Implement SocialMediaAuditable protocol methods
    def get_og_title(self) -> str:
        """Return OpenGraph title."""
        return self.get_seo_title()

    def get_og_description(self) -> str:
        """Return OpenGraph description."""
        return self.get_meta_description()

    def get_og_image_url(self) -> str | None:
        """Return None (no OG image on this model)."""
        return None

    def get_og_type(self) -> str:
        """Return OpenGraph type."""
        return "website"

    def get_twitter_title(self) -> str:
        """Return Twitter title."""
        return self.get_og_title()

    def get_twitter_description(self) -> str:
        """Return Twitter description."""
        return self.get_og_description()

    def get_twitter_image_url(self) -> str | None:
        """Return None (no Twitter image on this model)."""
        return None

    def get_twitter_card_type(self) -> str:
        """Return Twitter card type."""
        return "summary"

    # Implement TechnicalSEOAuditable protocol methods
    def get_robots_directive(self) -> str:
        """Return robots directive."""
        return "index,follow" if self.is_published else "noindex,nofollow"

    def get_schema_type(self) -> str:
        """Return schema type."""
        return "WebPage"

    def get_schema_data(self) -> dict | None:
        """Return None (no additional schema data)."""
        return None

    def get_breadcrumb_title(self) -> str:
        """Return breadcrumb title."""
        return self.title

    def has_custom_canonical_url(self) -> bool:
        """Return False (using default get_absolute_url)."""
        return False

    # Implement ContentAuditable protocol methods
    def has_detailed_content(self) -> bool:
        """Check if page has substantial content."""
        return len(self.content) > 500

    def get_content_word_count(self) -> int:
        """Return word count of content."""
        return len(self.content.split())

    def get_content_sections_count(self) -> int:
        """Return number of content sections (count h2 tags as sections)."""
        return self.content.count("<h2>")

    def has_introduction_content(self) -> bool:
        """Check if page has introduction."""
        # Simple check: content has at least 100 characters
        return len(self.content) > 100

    def get_resource_count(self) -> int:
        """Return 0 (no resources on this simple model)."""
        return 0

    def get_featured_resource_count(self) -> int:
        """Return 0 (no featured resources)."""
        return 0
