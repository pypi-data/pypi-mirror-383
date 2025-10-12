"""Tests for all built-in SEO audit rules."""

from django.test import SimpleTestCase

from django_seo_audit.core import SEOStatus
from django_seo_audit.rules.content_rules import (
    ContentDepthRule,
    DetailedContentRule,
    IntroductionContentRule,
    ResourceCountRule,
)
from django_seo_audit.rules.core_seo_rules import (
    FocusKeyphraseRule,
    H1TagRule,
    MetaDescriptionLengthRule,
    SecondaryKeywordsRule,
    SEOTitleLengthRule,
)
from django_seo_audit.rules.social_media_rules import (
    OpenGraphDescriptionRule,
    OpenGraphImageRule,
    OpenGraphTitleRule,
    TwitterCardImageRule,
    TwitterCardTitleRule,
)
from django_seo_audit.rules.technical_seo_rules import (
    BreadcrumbOptimizationRule,
    CanonicalURLRule,
    RobotsDirectiveRule,
    StructuredDataRule,
)

# ==================== Core SEO Rules Tests ====================


class SEOTitleLengthRuleTest(SimpleTestCase):
    """Test SEO Title Length Rule."""

    def setUp(self):
        self.rule = SEOTitleLengthRule()

    def test_optimal_length(self):
        """Test title with optimal length (50-60 chars)."""

        class MockObj:
            def get_seo_title(self):
                return "A" * 55  # 55 chars - optimal

        result = self.rule.check(MockObj())
        self.assertEqual(result.status, SEOStatus.GOOD)
        self.assertEqual(result.score, 10)

    def test_slightly_short(self):
        """Test title slightly short (40-49 chars)."""

        class MockObj:
            def get_seo_title(self):
                return "A" * 45  # 45 chars

        result = self.rule.check(MockObj())
        self.assertEqual(result.status, SEOStatus.WARNING)
        self.assertEqual(result.score, 7)

    def test_slightly_long(self):
        """Test title slightly long (61-70 chars)."""

        class MockObj:
            def get_seo_title(self):
                return "A" * 65  # 65 chars

        result = self.rule.check(MockObj())
        self.assertEqual(result.status, SEOStatus.WARNING)
        self.assertEqual(result.score, 6)

    def test_too_short(self):
        """Test title too short (< 40 chars)."""

        class MockObj:
            def get_seo_title(self):
                return "Short"  # 5 chars

        result = self.rule.check(MockObj())
        self.assertEqual(result.status, SEOStatus.CRITICAL)
        self.assertEqual(result.score, 2)

    def test_too_long(self):
        """Test title too long (> 70 chars)."""

        class MockObj:
            def get_seo_title(self):
                return "A" * 100  # 100 chars

        result = self.rule.check(MockObj())
        self.assertEqual(result.status, SEOStatus.CRITICAL)
        self.assertEqual(result.score, 2)


class MetaDescriptionLengthRuleTest(SimpleTestCase):
    """Test Meta Description Length Rule."""

    def setUp(self):
        self.rule = MetaDescriptionLengthRule()

    def test_missing_description(self):
        """Test missing meta description."""

        class MockObj:
            def get_meta_description(self):
                return ""

        result = self.rule.check(MockObj())
        self.assertEqual(result.status, SEOStatus.CRITICAL)
        self.assertEqual(result.score, 0)

    def test_optimal_length(self):
        """Test description with optimal length (150-160 chars)."""

        class MockObj:
            def get_meta_description(self):
                return "A" * 155  # 155 chars

        result = self.rule.check(MockObj())
        self.assertEqual(result.status, SEOStatus.GOOD)
        self.assertEqual(result.score, 10)

    def test_slightly_short(self):
        """Test description slightly short (130-149 chars)."""

        class MockObj:
            def get_meta_description(self):
                return "A" * 140

        result = self.rule.check(MockObj())
        self.assertEqual(result.status, SEOStatus.WARNING)
        self.assertEqual(result.score, 7)

    def test_slightly_long(self):
        """Test description slightly long (161-180 chars)."""

        class MockObj:
            def get_meta_description(self):
                return "A" * 170

        result = self.rule.check(MockObj())
        self.assertEqual(result.status, SEOStatus.WARNING)
        self.assertEqual(result.score, 6)

    def test_too_short(self):
        """Test description too short (< 130 chars)."""

        class MockObj:
            def get_meta_description(self):
                return "Too short"

        result = self.rule.check(MockObj())
        self.assertEqual(result.status, SEOStatus.CRITICAL)
        self.assertEqual(result.score, 2)


class FocusKeyphraseRuleTest(SimpleTestCase):
    """Test Focus Keyphrase Rule."""

    def setUp(self):
        self.rule = FocusKeyphraseRule()

    def test_no_keyphrase(self):
        """Test missing focus keyphrase."""

        class MockObj:
            def get_focus_keyphrase(self):
                return ""

            def get_seo_title(self):
                return "Title"

            def get_meta_description(self):
                return "Description"

        result = self.rule.check(MockObj())
        self.assertEqual(result.status, SEOStatus.CRITICAL)
        self.assertEqual(result.score, 0)

    def test_keyphrase_in_both(self):
        """Test keyphrase in both title and description."""

        class MockObj:
            def get_focus_keyphrase(self):
                return "django seo"

            def get_seo_title(self):
                return "Django SEO Guide"

            def get_meta_description(self):
                return "Learn about Django SEO optimization"

        result = self.rule.check(MockObj())
        self.assertEqual(result.status, SEOStatus.GOOD)
        self.assertEqual(result.score, 10)

    def test_keyphrase_in_title_only(self):
        """Test keyphrase only in title."""

        class MockObj:
            def get_focus_keyphrase(self):
                return "django"

            def get_seo_title(self):
                return "Django Guide"

            def get_meta_description(self):
                return "A comprehensive guide"

        result = self.rule.check(MockObj())
        self.assertEqual(result.status, SEOStatus.WARNING)
        self.assertEqual(result.score, 7)

    def test_keyphrase_in_description_only(self):
        """Test keyphrase only in description."""

        class MockObj:
            def get_focus_keyphrase(self):
                return "python"

            def get_seo_title(self):
                return "Programming Guide"

            def get_meta_description(self):
                return "Learn Python programming"

        result = self.rule.check(MockObj())
        self.assertEqual(result.status, SEOStatus.WARNING)
        self.assertEqual(result.score, 6)

    def test_keyphrase_not_found(self):
        """Test keyphrase not in title or description."""

        class MockObj:
            def get_focus_keyphrase(self):
                return "ruby"

            def get_seo_title(self):
                return "Programming Guide"

            def get_meta_description(self):
                return "Learn programming"

        result = self.rule.check(MockObj())
        self.assertEqual(result.status, SEOStatus.CRITICAL)
        self.assertEqual(result.score, 2)


class H1TagRuleTest(SimpleTestCase):
    """Test H1 Tag Rule."""

    def setUp(self):
        self.rule = H1TagRule()

    def test_empty_h1(self):
        """Test empty H1 tag."""

        class MockObj:
            def get_h1_tag(self):
                return ""

            def get_seo_title(self):
                return "Title"

        result = self.rule.check(MockObj())
        self.assertEqual(result.status, SEOStatus.CRITICAL)
        self.assertEqual(result.score, 0)

    def test_h1_identical_to_title(self):
        """Test H1 identical to SEO title."""

        class MockObj:
            def get_h1_tag(self):
                return "Same Title"

            def get_seo_title(self):
                return "Same Title"

        result = self.rule.check(MockObj())
        self.assertEqual(result.status, SEOStatus.WARNING)
        self.assertEqual(result.score, 6)

    def test_h1_too_long(self):
        """Test H1 tag longer than 100 characters."""

        class MockObj:
            def get_h1_tag(self):
                return "A" * 120

            def get_seo_title(self):
                return "Different Title"

        result = self.rule.check(MockObj())
        self.assertEqual(result.status, SEOStatus.WARNING)
        self.assertEqual(result.score, 7)

    def test_h1_optimal(self):
        """Test well-optimized H1 tag."""

        class MockObj:
            def get_h1_tag(self):
                return "User-Friendly H1"

            def get_seo_title(self):
                return "SEO Optimized Title"

        result = self.rule.check(MockObj())
        self.assertEqual(result.status, SEOStatus.GOOD)
        self.assertEqual(result.score, 10)


class SecondaryKeywordsRuleTest(SimpleTestCase):
    """Test Secondary Keywords Rule."""

    def setUp(self):
        self.rule = SecondaryKeywordsRule()

    def test_no_keywords(self):
        """Test no secondary keywords."""

        class MockObj:
            def get_secondary_keywords(self):
                return ""

        result = self.rule.check(MockObj())
        self.assertEqual(result.status, SEOStatus.WARNING)
        self.assertEqual(result.score, 5)

    def test_optimal_count(self):
        """Test optimal keyword count (3-7)."""

        class MockObj:
            def get_secondary_keywords(self):
                return "python, django, web, framework, seo"

        result = self.rule.check(MockObj())
        self.assertEqual(result.status, SEOStatus.GOOD)
        self.assertEqual(result.score, 10)

    def test_few_keywords(self):
        """Test few keywords (1-2)."""

        class MockObj:
            def get_secondary_keywords(self):
                return "python, django"

        result = self.rule.check(MockObj())
        self.assertEqual(result.status, SEOStatus.WARNING)
        self.assertEqual(result.score, 7)

    def test_too_many_keywords(self):
        """Test too many keywords (> 7)."""

        class MockObj:
            def get_secondary_keywords(self):
                return "kw1, kw2, kw3, kw4, kw5, kw6, kw7, kw8, kw9"

        result = self.rule.check(MockObj())
        self.assertEqual(result.status, SEOStatus.WARNING)
        self.assertEqual(result.score, 6)


# ==================== Social Media Rules Tests ====================


class OpenGraphImageRuleTest(SimpleTestCase):
    """Test OpenGraph Image Rule."""

    def setUp(self):
        self.rule = OpenGraphImageRule()

    def test_no_image(self):
        """Test missing OG image."""

        class MockObj:
            def get_og_image_url(self):
                return None

        result = self.rule.check(MockObj())
        self.assertEqual(result.status, SEOStatus.WARNING)
        self.assertEqual(result.score, 4)

    def test_image_present(self):
        """Test OG image is present."""

        class MockObj:
            def get_og_image_url(self):
                return "https://example.com/image.jpg"

        result = self.rule.check(MockObj())
        self.assertEqual(result.status, SEOStatus.GOOD)
        self.assertEqual(result.score, 10)


class OpenGraphTitleRuleTest(SimpleTestCase):
    """Test OpenGraph Title Rule."""

    def setUp(self):
        self.rule = OpenGraphTitleRule()

    def test_empty_title(self):
        """Test empty OG title."""

        class MockObj:
            def get_og_title(self):
                return ""

        result = self.rule.check(MockObj())
        self.assertEqual(result.status, SEOStatus.WARNING)
        self.assertEqual(result.score, 6)

    def test_optimal_length(self):
        """Test optimal OG title length (40-95 chars)."""

        class MockObj:
            def get_og_title(self):
                return "A" * 60

        result = self.rule.check(MockObj())
        self.assertEqual(result.status, SEOStatus.GOOD)
        self.assertEqual(result.score, 10)

    def test_short_title(self):
        """Test short OG title (< 40 chars)."""

        class MockObj:
            def get_og_title(self):
                return "Short Title"

        result = self.rule.check(MockObj())
        self.assertEqual(result.status, SEOStatus.WARNING)
        self.assertEqual(result.score, 7)

    def test_long_title(self):
        """Test long OG title (> 95 chars)."""

        class MockObj:
            def get_og_title(self):
                return "A" * 120

        result = self.rule.check(MockObj())
        self.assertEqual(result.status, SEOStatus.WARNING)
        self.assertEqual(result.score, 5)


class OpenGraphDescriptionRuleTest(SimpleTestCase):
    """Test OpenGraph Description Rule."""

    def setUp(self):
        self.rule = OpenGraphDescriptionRule()

    def test_empty_description(self):
        """Test empty OG description."""

        class MockObj:
            def get_og_description(self):
                return ""

        result = self.rule.check(MockObj())
        self.assertEqual(result.status, SEOStatus.WARNING)
        self.assertEqual(result.score, 6)

    def test_optimal_length(self):
        """Test optimal OG description length (150-200 chars)."""

        class MockObj:
            def get_og_description(self):
                return "A" * 175

        result = self.rule.check(MockObj())
        self.assertEqual(result.status, SEOStatus.GOOD)
        self.assertEqual(result.score, 10)

    def test_short_description(self):
        """Test short OG description."""

        class MockObj:
            def get_og_description(self):
                return "A" * 100

        result = self.rule.check(MockObj())
        self.assertEqual(result.status, SEOStatus.GOOD)
        self.assertEqual(result.score, 10)

    def test_long_description(self):
        """Test long OG description."""

        class MockObj:
            def get_og_description(self):
                return "A" * 250

        result = self.rule.check(MockObj())
        self.assertEqual(result.status, SEOStatus.WARNING)
        self.assertEqual(result.score, 5)


class TwitterCardImageRuleTest(SimpleTestCase):
    """Test Twitter Card Image Rule."""

    def setUp(self):
        self.rule = TwitterCardImageRule()

    def test_no_image(self):
        """Test missing Twitter image and no OG image."""

        class MockObj:
            def get_twitter_image_url(self):
                return None

            def get_og_image_url(self):
                return None

        result = self.rule.check(MockObj())
        self.assertEqual(result.status, SEOStatus.WARNING)
        self.assertEqual(result.score, 4)

    def test_image_present(self):
        """Test Twitter image is present."""

        class MockObj:
            def get_twitter_image_url(self):
                return "https://example.com/twitter.jpg"

            def get_og_image_url(self):
                return None

        result = self.rule.check(MockObj())
        self.assertEqual(result.status, SEOStatus.GOOD)
        self.assertEqual(result.score, 10)


class TwitterCardTitleRuleTest(SimpleTestCase):
    """Test Twitter Card Title Rule."""

    def setUp(self):
        self.rule = TwitterCardTitleRule()

    def test_empty_title(self):
        """Test empty Twitter title."""

        class MockObj:
            def get_twitter_title(self):
                return ""

        result = self.rule.check(MockObj())
        self.assertEqual(result.status, SEOStatus.WARNING)
        self.assertEqual(result.score, 6)

    def test_optimal_length(self):
        """Test optimal Twitter title length (40-70 chars)."""

        class MockObj:
            def get_twitter_title(self):
                return "A" * 55

        result = self.rule.check(MockObj())
        self.assertEqual(result.status, SEOStatus.GOOD)
        self.assertEqual(result.score, 10)

    def test_short_title(self):
        """Test short Twitter title."""

        class MockObj:
            def get_twitter_title(self):
                return "Short"

        result = self.rule.check(MockObj())
        self.assertEqual(result.status, SEOStatus.WARNING)
        self.assertEqual(result.score, 7)

    def test_long_title(self):
        """Test long Twitter title."""

        class MockObj:
            def get_twitter_title(self):
                return "A" * 100

        result = self.rule.check(MockObj())
        self.assertEqual(result.status, SEOStatus.WARNING)
        self.assertEqual(result.score, 5)


# ==================== Content Rules Tests ====================


class DetailedContentRuleTest(SimpleTestCase):
    """Test Detailed Content Rule."""

    def setUp(self):
        self.rule = DetailedContentRule()

    def test_has_detailed_content(self):
        """Test object has detailed content."""

        class MockObj:
            def has_detailed_content(self):
                return True

            def get_content_sections_count(self):
                return 5

            def get_content_word_count(self):
                return 600

        result = self.rule.check(MockObj())
        self.assertEqual(result.status, SEOStatus.GOOD)
        self.assertEqual(result.score, 10)

    def test_no_detailed_content_but_sections(self):
        """Test no detailed content but has some sections."""

        class MockObj:
            def has_detailed_content(self):
                return False

            def get_content_sections_count(self):
                return 3

            def get_content_word_count(self):
                return 350

        result = self.rule.check(MockObj())
        self.assertEqual(result.status, SEOStatus.CRITICAL)
        self.assertEqual(result.score, 0)

    def test_minimal_content(self):
        """Test minimal content."""

        class MockObj:
            def has_detailed_content(self):
                return False

            def get_content_sections_count(self):
                return 2

            def get_content_word_count(self):
                return 200

        result = self.rule.check(MockObj())
        self.assertEqual(result.status, SEOStatus.CRITICAL)
        self.assertEqual(result.score, 0)


class IntroductionContentRuleTest(SimpleTestCase):
    """Test Introduction Content Rule."""

    def setUp(self):
        self.rule = IntroductionContentRule()

    def test_has_introduction(self):
        """Test object has introduction content."""

        class MockObj:
            def has_introduction_content(self):
                return True

        result = self.rule.check(MockObj())
        self.assertEqual(result.status, SEOStatus.GOOD)
        self.assertEqual(result.score, 10)

    def test_no_introduction(self):
        """Test object lacks introduction content."""

        class MockObj:
            def has_introduction_content(self):
                return False

        result = self.rule.check(MockObj())
        self.assertEqual(result.status, SEOStatus.CRITICAL)
        self.assertEqual(result.score, 0)


class ResourceCountRuleTest(SimpleTestCase):
    """Test Resource Count Rule."""

    def setUp(self):
        self.rule = ResourceCountRule()

    def test_many_resources(self):
        """Test with many resources (>= 10)."""

        class MockObj:
            def get_resource_count(self):
                return 15

            def get_featured_resource_count(self):
                return 5

        result = self.rule.check(MockObj())
        self.assertEqual(result.status, SEOStatus.GOOD)
        self.assertEqual(result.score, 10)

    def test_moderate_resources(self):
        """Test with moderate resources (5-9)."""

        class MockObj:
            def get_resource_count(self):
                return 7

            def get_featured_resource_count(self):
                return 2

        result = self.rule.check(MockObj())
        self.assertEqual(result.status, SEOStatus.GOOD)
        self.assertEqual(result.score, 10)

    def test_few_resources(self):
        """Test with few resources (1-2)."""

        class MockObj:
            def get_resource_count(self):
                return 2

            def get_featured_resource_count(self):
                return 0

        result = self.rule.check(MockObj())
        self.assertEqual(result.status, SEOStatus.WARNING)
        self.assertEqual(result.score, 6)

    def test_no_resources(self):
        """Test with no resources."""

        class MockObj:
            def get_resource_count(self):
                return 0

            def get_featured_resource_count(self):
                return 0

        result = self.rule.check(MockObj())
        self.assertEqual(result.status, SEOStatus.WARNING)
        self.assertEqual(result.score, 4)


class ContentDepthRuleTest(SimpleTestCase):
    """Test Content Depth Rule."""

    def setUp(self):
        self.rule = ContentDepthRule()

    def test_comprehensive_content(self):
        """Test comprehensive content (>= 800 words, 6 sections)."""

        class MockObj:
            def get_content_word_count(self):
                return 900

            def get_content_sections_count(self):
                return 7

        result = self.rule.check(MockObj())
        self.assertEqual(result.status, SEOStatus.GOOD)
        self.assertEqual(result.score, 10)

    def test_substantial_content(self):
        """Test substantial content (500-799 words, 4 sections)."""

        class MockObj:
            def get_content_word_count(self):
                return 600

            def get_content_sections_count(self):
                return 5

        result = self.rule.check(MockObj())
        self.assertEqual(result.status, SEOStatus.GOOD)
        self.assertEqual(result.score, 8)

    def test_minimal_content(self):
        """Test minimal content (300-499 words, 3 sections)."""

        class MockObj:
            def get_content_word_count(self):
                return 350

            def get_content_sections_count(self):
                return 3

        result = self.rule.check(MockObj())
        self.assertEqual(result.status, SEOStatus.WARNING)
        self.assertEqual(result.score, 6)

    def test_very_little_content(self):
        """Test very little content (< 300 words)."""

        class MockObj:
            def get_content_word_count(self):
                return 200

            def get_content_sections_count(self):
                return 2

        result = self.rule.check(MockObj())
        self.assertEqual(result.status, SEOStatus.CRITICAL)
        self.assertEqual(result.score, 3)


# ==================== Technical SEO Rules Tests ====================


class CanonicalURLRuleTest(SimpleTestCase):
    """Test Canonical URL Rule."""

    def setUp(self):
        self.rule = CanonicalURLRule()

    def test_canonical_url_set(self):
        """Test canonical URL is set."""

        class MockObj:
            def get_canonical_url(self):
                return "https://example.com/page"

            def has_custom_canonical_url(self):
                return True

        result = self.rule.check(MockObj())
        self.assertEqual(result.status, SEOStatus.GOOD)
        self.assertEqual(result.score, 10)

    def test_canonical_url_missing(self):
        """Test canonical URL uses default (system provides it)."""

        class MockObj:
            def get_canonical_url(self):
                return "https://example.com/default"

            def has_custom_canonical_url(self):
                return False

        result = self.rule.check(MockObj())
        self.assertEqual(result.status, SEOStatus.GOOD)
        self.assertEqual(result.score, 9)


class RobotsDirectiveRuleTest(SimpleTestCase):
    """Test Robots Directive Rule."""

    def setUp(self):
        self.rule = RobotsDirectiveRule()

    def test_indexable_directive(self):
        """Test indexable robots directive."""

        class MockObj:
            def get_robots_directive(self):
                return "index,follow"

        result = self.rule.check(MockObj())
        self.assertEqual(result.status, SEOStatus.GOOD)
        self.assertEqual(result.score, 10)

    def test_noindex_directive(self):
        """Test noindex robots directive."""

        class MockObj:
            def get_robots_directive(self):
                return "noindex,nofollow"

        result = self.rule.check(MockObj())
        self.assertEqual(result.status, SEOStatus.CRITICAL)
        self.assertEqual(result.score, 0)

    def test_partial_noindex(self):
        """Test partial noindex directive."""

        class MockObj:
            def get_robots_directive(self):
                return "noindex,follow"

        result = self.rule.check(MockObj())
        self.assertEqual(result.status, SEOStatus.CRITICAL)
        self.assertEqual(result.score, 0)


class StructuredDataRuleTest(SimpleTestCase):
    """Test Structured Data Rule."""

    def setUp(self):
        self.rule = StructuredDataRule()

    def test_schema_type_set(self):
        """Test schema type is set without additional data."""

        class MockObj:
            def get_schema_type(self):
                return "Article"

            def get_schema_data(self):
                return None

        result = self.rule.check(MockObj())
        self.assertEqual(result.status, SEOStatus.GOOD)
        self.assertEqual(result.score, 8)

    def test_schema_with_additional_data(self):
        """Test schema with additional structured data."""

        class MockObj:
            def get_schema_type(self):
                return "Article"

            def get_schema_data(self):
                return {"author": "John Doe"}

        result = self.rule.check(MockObj())
        self.assertEqual(result.status, SEOStatus.GOOD)
        self.assertEqual(result.score, 10)

    def test_no_schema_type(self):
        """Test missing schema type."""

        class MockObj:
            def get_schema_type(self):
                return ""

            def get_schema_data(self):
                return None

        result = self.rule.check(MockObj())
        self.assertEqual(result.status, SEOStatus.WARNING)
        self.assertEqual(result.score, 4)


class BreadcrumbOptimizationRuleTest(SimpleTestCase):
    """Test Breadcrumb Optimization Rule."""

    def setUp(self):
        self.rule = BreadcrumbOptimizationRule()

    def test_breadcrumb_title_set(self):
        """Test breadcrumb title is set."""

        class MockObj:
            def get_breadcrumb_title(self):
                return "Breadcrumb Title"

        result = self.rule.check(MockObj())
        self.assertEqual(result.status, SEOStatus.GOOD)
        self.assertEqual(result.score, 10)

    def test_breadcrumb_title_missing(self):
        """Test breadcrumb title is missing."""

        class MockObj:
            def get_breadcrumb_title(self):
                return ""

        result = self.rule.check(MockObj())
        self.assertEqual(result.status, SEOStatus.WARNING)
        self.assertEqual(result.score, 6)


# ==================== Rule Metadata Tests ====================


class RuleMetadataTest(SimpleTestCase):
    """Test that all rules have proper metadata."""

    def test_all_rules_have_name(self):
        """Test all rules have a name."""
        rules = [
            SEOTitleLengthRule,
            MetaDescriptionLengthRule,
            FocusKeyphraseRule,
            H1TagRule,
            SecondaryKeywordsRule,
            OpenGraphImageRule,
            OpenGraphTitleRule,
            OpenGraphDescriptionRule,
            TwitterCardImageRule,
            TwitterCardTitleRule,
            DetailedContentRule,
            IntroductionContentRule,
            ResourceCountRule,
            ContentDepthRule,
            CanonicalURLRule,
            RobotsDirectiveRule,
            StructuredDataRule,
            BreadcrumbOptimizationRule,
        ]

        for rule_class in rules:
            with self.subTest(rule=rule_class.__name__):
                self.assertTrue(rule_class.name)
                self.assertNotEqual(rule_class.name, "")

    def test_all_rules_have_category(self):
        """Test all rules have a category."""
        rules = [
            (SEOTitleLengthRule, "core_seo"),
            (MetaDescriptionLengthRule, "core_seo"),
            (FocusKeyphraseRule, "core_seo"),
            (H1TagRule, "core_seo"),
            (SecondaryKeywordsRule, "core_seo"),
            (OpenGraphImageRule, "social_media"),
            (OpenGraphTitleRule, "social_media"),
            (OpenGraphDescriptionRule, "social_media"),
            (TwitterCardImageRule, "social_media"),
            (TwitterCardTitleRule, "social_media"),
            (DetailedContentRule, "content"),
            (IntroductionContentRule, "content"),
            (ResourceCountRule, "content"),
            (ContentDepthRule, "content"),
            (CanonicalURLRule, "technical_seo"),
            (RobotsDirectiveRule, "technical_seo"),
            (StructuredDataRule, "technical_seo"),
            (BreadcrumbOptimizationRule, "technical_seo"),
        ]

        for rule_class, expected_category in rules:
            with self.subTest(rule=rule_class.__name__):
                self.assertEqual(rule_class.category, expected_category)

    def test_all_rules_have_weight(self):
        """Test all rules have a weight."""
        rules = [
            SEOTitleLengthRule,
            MetaDescriptionLengthRule,
            FocusKeyphraseRule,
            H1TagRule,
            SecondaryKeywordsRule,
            OpenGraphImageRule,
            OpenGraphTitleRule,
            OpenGraphDescriptionRule,
            TwitterCardImageRule,
            TwitterCardTitleRule,
            DetailedContentRule,
            IntroductionContentRule,
            ResourceCountRule,
            ContentDepthRule,
            CanonicalURLRule,
            RobotsDirectiveRule,
            StructuredDataRule,
            BreadcrumbOptimizationRule,
        ]

        for rule_class in rules:
            with self.subTest(rule=rule_class.__name__):
                self.assertGreaterEqual(rule_class.weight, 1)
                self.assertLessEqual(rule_class.weight, 5)
