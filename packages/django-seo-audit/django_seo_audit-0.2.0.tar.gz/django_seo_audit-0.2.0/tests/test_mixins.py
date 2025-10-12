"""Tests for SEOAuditableMixin with Django models."""

from django.test import TestCase

from tests.example_app.models import BlogPost, Product


class SEOAuditableMixinBasicTest(TestCase):
    """Test basic SEOAuditableMixin functionality."""

    def test_get_seo_title_with_seo_title_field(self):
        """Test get_seo_title returns seo_title when set."""
        post = BlogPost(title="My Post", seo_title="SEO Optimized Title")
        self.assertEqual(post.get_seo_title(), "SEO Optimized Title")

    def test_get_seo_title_fallback_to_name(self):
        """Test get_seo_title falls back to title when seo_title is empty."""
        post = BlogPost(title="My Post", seo_title="")
        self.assertEqual(post.get_seo_title(), "My Post")

    def test_get_seo_title_fallback_with_name_field(self):
        """Test get_seo_title falls back to name field on Product model."""
        product = Product(name="Widget", seo_title="")
        self.assertEqual(product.get_seo_title(), "Widget")

    def test_get_meta_description_with_field(self):
        """Test get_meta_description returns meta_description when set."""
        post = BlogPost(meta_description="A great post about SEO")
        self.assertEqual(post.get_meta_description(), "A great post about SEO")

    def test_get_meta_description_fallback(self):
        """Test get_meta_description falls back to short_description."""
        product = Product(
            name="Widget",
            meta_description="",
            short_description="A short description",
        )
        self.assertEqual(product.get_meta_description(), "A short description")

    def test_get_canonical_url_with_custom_url(self):
        """Test get_canonical_url returns custom canonical_url when set."""
        post = BlogPost(
            slug="test-post",
            canonical_url="https://example.com/canonical",
        )
        self.assertEqual(post.get_canonical_url(), "https://example.com/canonical")

    def test_get_canonical_url_fallback_to_absolute_url(self):
        """Test get_canonical_url falls back to get_absolute_url."""
        post = BlogPost(slug="test-post", canonical_url="")
        self.assertEqual(post.get_canonical_url(), "/blog/test-post/")

    def test_get_focus_keyphrase(self):
        """Test get_focus_keyphrase returns focus keyphrase."""
        post = BlogPost(focus_keyphrase="django seo")
        self.assertEqual(post.get_focus_keyphrase(), "django seo")

    def test_get_focus_keyphrase_empty(self):
        """Test get_focus_keyphrase returns empty string when not set."""
        post = BlogPost(focus_keyphrase="")
        self.assertEqual(post.get_focus_keyphrase(), "")

    def test_get_secondary_keywords(self):
        """Test get_secondary_keywords returns keywords."""
        post = BlogPost(secondary_keywords="python, web, framework")
        self.assertEqual(post.get_secondary_keywords(), "python, web, framework")

    def test_get_h1_tag_with_field(self):
        """Test get_h1_tag returns h1_tag when set."""
        post = BlogPost(title="Title", seo_title="SEO Title", h1_tag="Custom H1")
        self.assertEqual(post.get_h1_tag(), "Custom H1")

    def test_get_h1_tag_fallback_to_seo_title(self):
        """Test get_h1_tag falls back to seo_title."""
        post = BlogPost(title="Title", seo_title="SEO Title", h1_tag="")
        self.assertEqual(post.get_h1_tag(), "SEO Title")

    def test_get_h1_tag_fallback_to_title(self):
        """Test get_h1_tag falls back to title when seo_title also empty."""
        post = BlogPost(title="Title", seo_title="", h1_tag="")
        self.assertEqual(post.get_h1_tag(), "Title")


class SEOAuditableMixinSocialMediaTest(TestCase):
    """Test social media protocol methods."""

    def test_get_og_title_with_field(self):
        """Test get_og_title returns og_title when set."""
        post = BlogPost(seo_title="SEO Title", og_title="OG Title")
        self.assertEqual(post.get_og_title(), "OG Title")

    def test_get_og_title_fallback(self):
        """Test get_og_title falls back to seo_title."""
        post = BlogPost(title="Title", og_title="")
        self.assertEqual(post.get_og_title(), "Title")

    def test_get_og_description_with_field(self):
        """Test get_og_description returns og_description when set."""
        post = BlogPost(
            meta_description="Meta desc",
            og_description="OG description",
        )
        self.assertEqual(post.get_og_description(), "OG description")

    def test_get_og_description_fallback(self):
        """Test get_og_description falls back to meta_description."""
        post = BlogPost(meta_description="Meta desc", og_description="")
        self.assertEqual(post.get_og_description(), "Meta desc")

    def test_get_og_image_url_with_url_field(self):
        """Test get_og_image_url returns URL string."""
        post = BlogPost(og_image="https://example.com/image.jpg")
        self.assertEqual(post.get_og_image_url(), "https://example.com/image.jpg")

    def test_get_og_image_url_empty(self):
        """Test get_og_image_url returns None when not set."""
        post = BlogPost(og_image="")
        self.assertIsNone(post.get_og_image_url())

    def test_get_og_type_with_field(self):
        """Test get_og_type returns og_type."""
        post = BlogPost(og_type="article")
        self.assertEqual(post.get_og_type(), "article")

    def test_get_og_type_default(self):
        """Test get_og_type returns default value."""
        post = BlogPost(og_type="")
        self.assertEqual(post.get_og_type(), "article")

    def test_get_twitter_title_with_field(self):
        """Test get_twitter_title returns twitter_title when set."""
        post = BlogPost(
            og_title="OG Title",
            twitter_title="Twitter Title",
        )
        self.assertEqual(post.get_twitter_title(), "Twitter Title")

    def test_get_twitter_title_fallback(self):
        """Test get_twitter_title falls back to og_title."""
        post = BlogPost(og_title="OG Title", twitter_title="")
        self.assertEqual(post.get_twitter_title(), "OG Title")

    def test_get_twitter_description_with_field(self):
        """Test get_twitter_description returns twitter_description."""
        post = BlogPost(
            og_description="OG Desc",
            twitter_description="Twitter Desc",
        )
        self.assertEqual(post.get_twitter_description(), "Twitter Desc")

    def test_get_twitter_description_fallback(self):
        """Test get_twitter_description falls back to og_description."""
        post = BlogPost(og_description="OG Desc", twitter_description="")
        self.assertEqual(post.get_twitter_description(), "OG Desc")

    def test_get_twitter_image_url_with_url_field(self):
        """Test get_twitter_image_url returns URL string."""
        post = BlogPost(twitter_image="https://example.com/twitter.jpg")
        self.assertEqual(post.get_twitter_image_url(), "https://example.com/twitter.jpg")

    def test_get_twitter_image_url_empty(self):
        """Test get_twitter_image_url returns None when not set."""
        post = BlogPost(twitter_image="")
        self.assertIsNone(post.get_twitter_image_url())

    def test_get_twitter_card_type_with_field(self):
        """Test get_twitter_card_type returns twitter_card_type."""
        post = BlogPost(twitter_card_type="summary")
        self.assertEqual(post.get_twitter_card_type(), "summary")

    def test_get_twitter_card_type_default(self):
        """Test get_twitter_card_type returns default."""
        post = BlogPost(twitter_card_type="")
        self.assertEqual(post.get_twitter_card_type(), "summary_large_image")


class SEOAuditableMixinContentTest(TestCase):
    """Test content protocol methods."""

    def test_has_detailed_content_no_subpages(self):
        """Test has_detailed_content returns False when no subpages."""
        post = BlogPost(content="Some content")
        self.assertFalse(post.has_detailed_content())

    def test_get_content_word_count_no_subpages(self):
        """Test get_content_word_count returns 0 when no subpages."""
        post = BlogPost(content="Some content here")
        self.assertEqual(post.get_content_word_count(), 0)

    def test_get_content_sections_count_no_subpages(self):
        """Test get_content_sections_count returns 0 when no subpages."""
        post = BlogPost()
        self.assertEqual(post.get_content_sections_count(), 0)

    def test_has_introduction_content_no_subpages(self):
        """Test has_introduction_content returns False when no subpages."""
        post = BlogPost(content="Introduction here")
        self.assertFalse(post.has_introduction_content())

    def test_get_resource_count_no_resources(self):
        """Test get_resource_count returns 0 when no resources."""
        post = BlogPost()
        self.assertEqual(post.get_resource_count(), 0)

    def test_get_featured_resource_count_no_resources(self):
        """Test get_featured_resource_count returns 0 when no resources."""
        post = BlogPost()
        self.assertEqual(post.get_featured_resource_count(), 0)


class SEOAuditableMixinTechnicalTest(TestCase):
    """Test technical SEO protocol methods."""

    def test_get_robots_directive_with_field(self):
        """Test get_robots_directive returns robots_directive."""
        post = BlogPost(robots_directive="noindex,nofollow")
        self.assertEqual(post.get_robots_directive(), "noindex,nofollow")

    def test_get_robots_directive_default(self):
        """Test get_robots_directive returns default when empty."""
        post = BlogPost(robots_directive="")
        self.assertEqual(post.get_robots_directive(), "index,follow")

    def test_get_schema_type_with_field(self):
        """Test get_schema_type returns schema_type."""
        post = BlogPost(schema_type="BlogPosting")
        self.assertEqual(post.get_schema_type(), "BlogPosting")

    def test_get_schema_type_default(self):
        """Test get_schema_type returns default when empty."""
        post = BlogPost(schema_type="")
        self.assertEqual(post.get_schema_type(), "Article")

    def test_get_schema_data_with_dict(self):
        """Test get_schema_data returns dict when schema_data is dict."""
        schema = {"author": "John Doe", "datePublished": "2024-01-01"}
        post = BlogPost(schema_data=schema)
        self.assertEqual(post.get_schema_data(), schema)

    def test_get_schema_data_none(self):
        """Test get_schema_data returns None when not set."""
        post = BlogPost(schema_data=None)
        self.assertIsNone(post.get_schema_data())

    def test_get_breadcrumb_title_with_field(self):
        """Test get_breadcrumb_title returns breadcrumb_title when set."""
        post = BlogPost(title="Long Title", breadcrumb_title="Short")
        self.assertEqual(post.get_breadcrumb_title(), "Short")

    def test_get_breadcrumb_title_fallback(self):
        """Test get_breadcrumb_title falls back to title."""
        post = BlogPost(title="Title", breadcrumb_title="")
        self.assertEqual(post.get_breadcrumb_title(), "Title")

    def test_get_breadcrumb_title_fallback_to_name(self):
        """Test get_breadcrumb_title falls back to name on Product."""
        product = Product(name="Widget")
        self.assertEqual(product.get_breadcrumb_title(), "Widget")

    def test_has_custom_canonical_url_true(self):
        """Test has_custom_canonical_url returns True when URL is set."""
        post = BlogPost(canonical_url="https://example.com/custom")
        self.assertTrue(post.has_custom_canonical_url())

    def test_has_custom_canonical_url_false(self):
        """Test has_custom_canonical_url returns False when URL is empty."""
        post = BlogPost(canonical_url="")
        self.assertFalse(post.has_custom_canonical_url())

    def test_has_custom_canonical_url_whitespace(self):
        """Test has_custom_canonical_url returns False for whitespace."""
        post = BlogPost(canonical_url="   ")
        self.assertFalse(post.has_custom_canonical_url())


class SEOAuditableMixinUtilityTest(TestCase):
    """Test utility methods."""

    def test_get_structured_data(self):
        """Test get_structured_data returns proper JSON-LD structure."""
        post = BlogPost(
            title="Test Post",
            seo_title="SEO Test Post",
            meta_description="A test post",
            slug="test-post",
            schema_type="BlogPosting",
        )
        data = post.get_structured_data()

        self.assertEqual(data["@context"], "https://schema.org")
        self.assertEqual(data["@type"], "BlogPosting")
        self.assertEqual(data["name"], "SEO Test Post")
        self.assertEqual(data["description"], "A test post")
        self.assertEqual(data["url"], "/blog/test-post/")

    def test_get_structured_data_with_additional_schema(self):
        """Test get_structured_data merges additional schema data."""
        additional = {"author": "Jane Doe", "datePublished": "2024-01-01"}
        post = BlogPost(
            title="Test",
            slug="test",
            schema_type="Article",
            schema_data=additional,
        )
        data = post.get_structured_data()

        self.assertEqual(data["@type"], "Article")
        self.assertEqual(data["author"], "Jane Doe")
        self.assertEqual(data["datePublished"], "2024-01-01")

    def test_get_structured_data_json(self):
        """Test get_structured_data_json returns JSON string."""
        post = BlogPost(
            title="Test",
            slug="test",
            schema_type="Article",
        )
        json_str = post.get_structured_data_json()

        self.assertIsInstance(json_str, str)
        self.assertIn('"@context"', json_str)
        self.assertIn('"@type"', json_str)
        self.assertIn('"Article"', json_str)


class ProductModelMixinTest(TestCase):
    """Test mixin behavior on Product model (minimal fields)."""

    def test_product_seo_title_fallback_chain(self):
        """Test Product model fallback chain for seo_title."""
        # With seo_title
        product = Product(name="Widget", seo_title="Buy Widget Online")
        self.assertEqual(product.get_seo_title(), "Buy Widget Online")

        # Without seo_title, falls back to name
        product = Product(name="Widget", seo_title="")
        self.assertEqual(product.get_seo_title(), "Widget")

    def test_product_meta_description_fallback(self):
        """Test Product meta_description fallback to short_description."""
        # With meta_description
        product = Product(
            name="Widget",
            meta_description="Buy our widget",
            short_description="A widget",
        )
        self.assertEqual(product.get_meta_description(), "Buy our widget")

        # Without meta_description
        product = Product(
            name="Widget",
            meta_description="",
            short_description="A widget",
        )
        self.assertEqual(product.get_meta_description(), "A widget")

    def test_product_canonical_url(self):
        """Test Product canonical URL uses get_absolute_url."""
        product = Product(slug="widget")
        self.assertEqual(product.get_canonical_url(), "/products/widget/")

    def test_product_minimal_seo_fields(self):
        """Test Product works with minimal SEO fields."""
        product = Product(
            name="Widget",
            slug="widget",
            description="Description",
            price=19.99,
            sku="WID-001",
        )

        # Should not raise errors
        self.assertEqual(product.get_seo_title(), "Widget")
        self.assertEqual(product.get_meta_description(), "")
        self.assertEqual(product.get_canonical_url(), "/products/widget/")
        self.assertEqual(product.get_focus_keyphrase(), "")
        self.assertEqual(product.get_h1_tag(), "Widget")
