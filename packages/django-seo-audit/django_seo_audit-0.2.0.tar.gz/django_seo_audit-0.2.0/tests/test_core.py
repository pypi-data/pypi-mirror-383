"""Tests for core SEO audit components."""

from django.test import SimpleTestCase

from django_seo_audit.core import SEOResult, SEORule, SEOStatus


class SEOStatusTest(SimpleTestCase):
    """Test SEOStatus enum functionality."""

    def test_status_values(self):
        """Test status enum has expected values."""
        self.assertEqual(SEOStatus.GOOD.value, "good")
        self.assertEqual(SEOStatus.WARNING.value, "warning")
        self.assertEqual(SEOStatus.CRITICAL.value, "critical")

    def test_status_str(self):
        """Test string representation of status."""
        self.assertEqual(str(SEOStatus.GOOD), "good")
        self.assertEqual(str(SEOStatus.WARNING), "warning")
        self.assertEqual(str(SEOStatus.CRITICAL), "critical")

    def test_status_emoji(self):
        """Test emoji property returns correct emoji."""
        self.assertEqual(SEOStatus.GOOD.emoji, "🟢")
        self.assertEqual(SEOStatus.WARNING.emoji, "🟡")
        self.assertEqual(SEOStatus.CRITICAL.emoji, "🔴")

    def test_status_color_code(self):
        """Test color code property returns ANSI codes."""
        self.assertEqual(SEOStatus.GOOD.color_code, "\033[92m")
        self.assertEqual(SEOStatus.WARNING.color_code, "\033[93m")
        self.assertEqual(SEOStatus.CRITICAL.color_code, "\033[91m")


class SEOResultTest(SimpleTestCase):
    """Test SEOResult dataclass functionality."""

    def test_result_creation(self):
        """Test creating a valid SEOResult."""
        result = SEOResult(
            status=SEOStatus.GOOD,
            message="Title is optimal",
            details="60 characters",
            score=10,
            suggestions=["Keep it up!"],
        )
        self.assertEqual(result.status, SEOStatus.GOOD)
        self.assertEqual(result.message, "Title is optimal")
        self.assertEqual(result.details, "60 characters")
        self.assertEqual(result.score, 10)
        self.assertEqual(result.suggestions, ["Keep it up!"])

    def test_result_defaults(self):
        """Test SEOResult with default values."""
        result = SEOResult(status=SEOStatus.GOOD, message="All good")
        self.assertEqual(result.details, "")
        self.assertEqual(result.score, 0)
        self.assertIsNone(result.suggestions)

    def test_result_immutable(self):
        """Test that SEOResult is immutable (frozen dataclass)."""
        result = SEOResult(status=SEOStatus.GOOD, message="Test")
        with self.assertRaises(AttributeError):
            result.message = "Changed"

    def test_score_validation_valid(self):
        """Test score validation accepts valid scores."""
        for score in [0, 5, 10]:
            result = SEOResult(status=SEOStatus.GOOD, message="Test", score=score)
            self.assertEqual(result.score, score)

    def test_score_validation_too_low(self):
        """Test score validation rejects scores below 0."""
        with self.assertRaises(ValueError) as context:
            SEOResult(status=SEOStatus.GOOD, message="Test", score=-1)
        self.assertIn("Score must be 0-10", str(context.exception))

    def test_score_validation_too_high(self):
        """Test score validation rejects scores above 10."""
        with self.assertRaises(ValueError) as context:
            SEOResult(status=SEOStatus.GOOD, message="Test", score=11)
        self.assertIn("Score must be 0-10", str(context.exception))

    def test_message_validation_empty(self):
        """Test message validation rejects empty messages."""
        with self.assertRaises(ValueError) as context:
            SEOResult(status=SEOStatus.GOOD, message="")
        self.assertIn("Message cannot be empty", str(context.exception))

    def test_message_validation_whitespace(self):
        """Test message validation rejects whitespace-only messages."""
        with self.assertRaises(ValueError) as context:
            SEOResult(status=SEOStatus.GOOD, message="   ")
        self.assertIn("Message cannot be empty", str(context.exception))

    def test_is_passing_good(self):
        """Test is_passing returns True for GOOD status."""
        result = SEOResult(status=SEOStatus.GOOD, message="Test")
        self.assertTrue(result.is_passing)

    def test_is_passing_warning(self):
        """Test is_passing returns True for WARNING status."""
        result = SEOResult(status=SEOStatus.WARNING, message="Test")
        self.assertTrue(result.is_passing)

    def test_is_passing_critical(self):
        """Test is_passing returns False for CRITICAL status."""
        result = SEOResult(status=SEOStatus.CRITICAL, message="Test")
        self.assertFalse(result.is_passing)

    def test_display_message_basic(self):
        """Test display_message with basic message."""
        result = SEOResult(status=SEOStatus.GOOD, message="Title optimal")
        self.assertEqual(result.display_message, "🟢 Title optimal")

    def test_display_message_with_details(self):
        """Test display_message includes details."""
        result = SEOResult(
            status=SEOStatus.WARNING,
            message="Title could be longer",
            details="45/50-60 chars",
        )
        self.assertEqual(result.display_message, "🟡 Title could be longer (45/50-60 chars)")

    def test_get_suggestions_text_none(self):
        """Test get_suggestions_text when suggestions is None."""
        result = SEOResult(status=SEOStatus.GOOD, message="Test")
        self.assertEqual(result.get_suggestions_text(), "")

    def test_get_suggestions_text_empty_list(self):
        """Test get_suggestions_text when suggestions is empty list."""
        result = SEOResult(status=SEOStatus.GOOD, message="Test", suggestions=[])
        self.assertEqual(result.get_suggestions_text(), "")

    def test_get_suggestions_text_with_suggestions(self):
        """Test get_suggestions_text formats suggestions properly."""
        result = SEOResult(
            status=SEOStatus.WARNING,
            message="Test",
            suggestions=["Add keywords", "Increase length"],
        )
        text = result.get_suggestions_text()
        self.assertIn("Suggestions:", text)
        self.assertIn("• Add keywords", text)
        self.assertIn("• Increase length", text)


class SEORuleTest(SimpleTestCase):
    """Test SEORule abstract base class."""

    def test_rule_attributes(self):
        """Test that SEORule has required class attributes."""
        self.assertTrue(hasattr(SEORule, "name"))
        self.assertTrue(hasattr(SEORule, "description"))
        self.assertTrue(hasattr(SEORule, "category"))
        self.assertTrue(hasattr(SEORule, "weight"))

    def test_rule_default_values(self):
        """Test default values for rule attributes."""
        self.assertEqual(SEORule.name, "")
        self.assertEqual(SEORule.description, "")
        self.assertEqual(SEORule.category, "general")
        self.assertEqual(SEORule.weight, 1)

    def test_rule_str(self):
        """Test string representation of rule."""

        class TestRuleStr(SEORule):
            name = "Test Rule Str"
            category = "test"

            def check(self, obj):
                return SEOResult(status=SEOStatus.GOOD, message="Test")

        rule = TestRuleStr()
        self.assertEqual(str(rule), "TestRuleStr(name='Test Rule Str', category='test')")

    def test_rule_repr(self):
        """Test detailed representation of rule."""

        class TestRuleRepr(SEORule):
            name = "Test Rule Repr"
            category = "test"
            weight = 3

            def check(self, obj):
                return SEOResult(status=SEOStatus.GOOD, message="Test")

        rule = TestRuleRepr()
        self.assertEqual(repr(rule), "TestRuleRepr(name='Test Rule Repr', category='test', weight=3)")

    def test_rule_get_protocol_requirements_default(self):
        """Test get_protocol_requirements returns empty list by default."""

        class TestRuleProtocol(SEORule):
            name = "Test Rule Protocol"

            def check(self, obj):
                return SEOResult(status=SEOStatus.GOOD, message="Test")

        self.assertEqual(TestRuleProtocol.get_protocol_requirements(), [])

    def test_rule_is_applicable_to_default(self):
        """Test is_applicable_to returns True by default."""

        class TestRuleApplicable(SEORule):
            name = "Test Rule Applicable"

            def check(self, obj):
                return SEOResult(status=SEOStatus.GOOD, message="Test")

        rule = TestRuleApplicable()
        self.assertTrue(rule.is_applicable_to(object()))

    def test_rule_check_must_be_implemented(self):
        """Test that check() must be implemented by subclasses."""
        # Can't instantiate abstract class without check() implementation
        # This test just verifies the error message
        with self.assertRaises(TypeError) as context:

            class TestRuleAbstract(SEORule):
                name = "Test Rule Abstract"

            TestRuleAbstract()

        self.assertIn("abstract", str(context.exception).lower())
