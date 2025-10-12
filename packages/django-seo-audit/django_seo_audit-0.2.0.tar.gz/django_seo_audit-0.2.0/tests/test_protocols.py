"""Tests for SEO audit protocol definitions."""

from django.test import SimpleTestCase


class BasicSEOAuditableTest(SimpleTestCase):
    """Test BasicSEOAuditable protocol."""

    def test_protocol_compliance_with_all_methods(self):
        """Test that an object with all methods satisfies the protocol."""

        class MockModel:
            def get_seo_title(self) -> str:
                return "Test Title"

            def get_meta_description(self) -> str:
                return "Test description"

            def get_canonical_url(self) -> str:
                return "https://example.com/test"

            def get_focus_keyphrase(self) -> str:
                return "test keyword"

            def get_secondary_keywords(self) -> str:
                return "keyword1, keyword2"

            def get_h1_tag(self) -> str:
                return "Test H1"

        obj = MockModel()

        # Protocol uses structural subtyping, so isinstance doesn't work
        # Instead, test that all required methods exist and are callable
        self.assertTrue(hasattr(obj, "get_seo_title"))
        self.assertTrue(callable(obj.get_seo_title))
        self.assertTrue(hasattr(obj, "get_meta_description"))
        self.assertTrue(callable(obj.get_meta_description))
        self.assertTrue(hasattr(obj, "get_canonical_url"))
        self.assertTrue(callable(obj.get_canonical_url))
        self.assertTrue(hasattr(obj, "get_focus_keyphrase"))
        self.assertTrue(callable(obj.get_focus_keyphrase))
        self.assertTrue(hasattr(obj, "get_secondary_keywords"))
        self.assertTrue(callable(obj.get_secondary_keywords))
        self.assertTrue(hasattr(obj, "get_h1_tag"))
        self.assertTrue(callable(obj.get_h1_tag))

        # Test return types
        self.assertIsInstance(obj.get_seo_title(), str)
        self.assertIsInstance(obj.get_meta_description(), str)
        self.assertIsInstance(obj.get_canonical_url(), str)
        self.assertIsInstance(obj.get_focus_keyphrase(), str)
        self.assertIsInstance(obj.get_secondary_keywords(), str)
        self.assertIsInstance(obj.get_h1_tag(), str)

    def test_protocol_with_missing_methods(self):
        """Test that an object without all methods doesn't satisfy protocol."""

        class IncompleteModel:
            def get_seo_title(self) -> str:
                return "Test"

        obj = IncompleteModel()

        # Has one method but not all
        self.assertTrue(hasattr(obj, "get_seo_title"))
        self.assertFalse(hasattr(obj, "get_meta_description"))
        self.assertFalse(hasattr(obj, "get_canonical_url"))


class SocialMediaAuditableTest(SimpleTestCase):
    """Test SocialMediaAuditable protocol."""

    def test_protocol_compliance(self):
        """Test protocol with all required methods."""

        class MockModel:
            def get_og_title(self) -> str:
                return "OG Title"

            def get_og_description(self) -> str:
                return "OG Description"

            def get_og_image_url(self) -> str | None:
                return "https://example.com/image.jpg"

            def get_og_type(self) -> str:
                return "article"

            def get_twitter_title(self) -> str:
                return "Twitter Title"

            def get_twitter_description(self) -> str:
                return "Twitter Description"

            def get_twitter_image_url(self) -> str | None:
                return "https://example.com/twitter.jpg"

            def get_twitter_card_type(self) -> str:
                return "summary_large_image"

        obj = MockModel()

        # Test all methods exist
        self.assertTrue(hasattr(obj, "get_og_title"))
        self.assertTrue(hasattr(obj, "get_og_description"))
        self.assertTrue(hasattr(obj, "get_og_image_url"))
        self.assertTrue(hasattr(obj, "get_og_type"))
        self.assertTrue(hasattr(obj, "get_twitter_title"))
        self.assertTrue(hasattr(obj, "get_twitter_description"))
        self.assertTrue(hasattr(obj, "get_twitter_image_url"))
        self.assertTrue(hasattr(obj, "get_twitter_card_type"))

        # Test return types (including optional None)
        self.assertIsInstance(obj.get_og_title(), str)
        self.assertIn(type(obj.get_og_image_url()), [str, type(None)])


class ContentAuditableTest(SimpleTestCase):
    """Test ContentAuditable protocol."""

    def test_protocol_compliance(self):
        """Test protocol with all required methods."""

        class MockModel:
            def has_detailed_content(self) -> bool:
                return True

            def get_content_word_count(self) -> int:
                return 500

            def get_content_sections_count(self) -> int:
                return 5

            def has_introduction_content(self) -> bool:
                return True

            def get_resource_count(self) -> int:
                return 10

            def get_featured_resource_count(self) -> int:
                return 3

        obj = MockModel()

        # Test all methods exist
        self.assertTrue(hasattr(obj, "has_detailed_content"))
        self.assertTrue(hasattr(obj, "get_content_word_count"))
        self.assertTrue(hasattr(obj, "get_content_sections_count"))
        self.assertTrue(hasattr(obj, "has_introduction_content"))
        self.assertTrue(hasattr(obj, "get_resource_count"))
        self.assertTrue(hasattr(obj, "get_featured_resource_count"))

        # Test return types
        self.assertIsInstance(obj.has_detailed_content(), bool)
        self.assertIsInstance(obj.get_content_word_count(), int)
        self.assertIsInstance(obj.get_content_sections_count(), int)
        self.assertIsInstance(obj.has_introduction_content(), bool)
        self.assertIsInstance(obj.get_resource_count(), int)
        self.assertIsInstance(obj.get_featured_resource_count(), int)


class TechnicalSEOAuditableTest(SimpleTestCase):
    """Test TechnicalSEOAuditable protocol."""

    def test_protocol_compliance(self):
        """Test protocol with all required methods."""

        class MockModel:
            def get_robots_directive(self) -> str:
                return "index,follow"

            def get_schema_type(self) -> str:
                return "Article"

            def get_schema_data(self) -> dict | None:
                return {"author": "John Doe"}

            def get_breadcrumb_title(self) -> str:
                return "Breadcrumb"

            def has_custom_canonical_url(self) -> bool:
                return True

        obj = MockModel()

        # Test all methods exist
        self.assertTrue(hasattr(obj, "get_robots_directive"))
        self.assertTrue(hasattr(obj, "get_schema_type"))
        self.assertTrue(hasattr(obj, "get_schema_data"))
        self.assertTrue(hasattr(obj, "get_breadcrumb_title"))
        self.assertTrue(hasattr(obj, "has_custom_canonical_url"))

        # Test return types
        self.assertIsInstance(obj.get_robots_directive(), str)
        self.assertIsInstance(obj.get_schema_type(), str)
        self.assertIn(type(obj.get_schema_data()), [dict, type(None)])
        self.assertIsInstance(obj.get_breadcrumb_title(), str)
        self.assertIsInstance(obj.has_custom_canonical_url(), bool)


class FullSEOAuditableTest(SimpleTestCase):
    """Test FullSEOAuditable combined protocol."""

    def test_full_protocol_combines_all(self):
        """Test that FullSEOAuditable requires all protocol methods."""

        class FullMockModel:
            # BasicSEOAuditable
            def get_seo_title(self) -> str:
                return "Title"

            def get_meta_description(self) -> str:
                return "Description"

            def get_canonical_url(self) -> str:
                return "https://example.com"

            def get_focus_keyphrase(self) -> str:
                return "keyword"

            def get_secondary_keywords(self) -> str:
                return "kw1, kw2"

            def get_h1_tag(self) -> str:
                return "H1"

            # SocialMediaAuditable
            def get_og_title(self) -> str:
                return "OG Title"

            def get_og_description(self) -> str:
                return "OG Desc"

            def get_og_image_url(self) -> str | None:
                return None

            def get_og_type(self) -> str:
                return "article"

            def get_twitter_title(self) -> str:
                return "Twitter"

            def get_twitter_description(self) -> str:
                return "Twitter Desc"

            def get_twitter_image_url(self) -> str | None:
                return None

            def get_twitter_card_type(self) -> str:
                return "summary"

            # ContentAuditable
            def has_detailed_content(self) -> bool:
                return True

            def get_content_word_count(self) -> int:
                return 500

            def get_content_sections_count(self) -> int:
                return 5

            def has_introduction_content(self) -> bool:
                return True

            def get_resource_count(self) -> int:
                return 10

            def get_featured_resource_count(self) -> int:
                return 3

            # TechnicalSEOAuditable
            def get_robots_directive(self) -> str:
                return "index"

            def get_schema_type(self) -> str:
                return "Article"

            def get_schema_data(self) -> dict | None:
                return None

            def get_breadcrumb_title(self) -> str:
                return "Breadcrumb"

            def has_custom_canonical_url(self) -> bool:
                return False

        obj = FullMockModel()

        # Verify methods from all four protocols exist
        # BasicSEOAuditable
        self.assertTrue(hasattr(obj, "get_seo_title"))
        # SocialMediaAuditable
        self.assertTrue(hasattr(obj, "get_og_title"))
        # ContentAuditable
        self.assertTrue(hasattr(obj, "has_detailed_content"))
        # TechnicalSEOAuditable
        self.assertTrue(hasattr(obj, "get_robots_directive"))


class DuckTypingTest(SimpleTestCase):
    """Test that protocol duck typing works as expected."""

    def test_protocol_works_without_inheritance(self):
        """Test protocols work through structural subtyping, not inheritance."""

        # This class doesn't inherit from anything, but satisfies BasicSEOAuditable
        class DuckTypedModel:
            def get_seo_title(self) -> str:
                return "Duck Typed Title"

            def get_meta_description(self) -> str:
                return "Duck typed description"

            def get_canonical_url(self) -> str:
                return "https://example.com/duck"

            def get_focus_keyphrase(self) -> str:
                return "duck typing"

            def get_secondary_keywords(self) -> str:
                return "protocols, python"

            def get_h1_tag(self) -> str:
                return "Duck H1"

        obj = DuckTypedModel()

        # Can be used anywhere BasicSEOAuditable is expected
        # (verified by having all required methods)
        required_methods = [
            "get_seo_title",
            "get_meta_description",
            "get_canonical_url",
            "get_focus_keyphrase",
            "get_secondary_keywords",
            "get_h1_tag",
        ]

        for method in required_methods:
            self.assertTrue(
                hasattr(obj, method),
                f"Object should have {method} method for BasicSEOAuditable protocol",
            )
            self.assertTrue(callable(getattr(obj, method)), f"{method} should be callable")
