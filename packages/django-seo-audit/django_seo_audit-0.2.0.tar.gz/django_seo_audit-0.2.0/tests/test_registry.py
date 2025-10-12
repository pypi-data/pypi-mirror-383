"""Tests for SEO rule registry and auditor."""

from django.test import SimpleTestCase

from django_seo_audit.core import SEOResult, SEORule, SEOStatus
from django_seo_audit.registry import SEOAuditor, SEOAuditResult, SEORuleRegistry


class SEORuleRegistryTest(SimpleTestCase):
    """Test SEORuleRegistry functionality."""

    def setUp(self):
        """Clear registry before each test."""
        SEORuleRegistry.clear()

    def tearDown(self):
        """Clear registry after each test."""
        SEORuleRegistry.clear()
        # Re-import rules to re-register them for other tests
        import django_seo_audit.rules  # noqa: F401

    def test_register_rule(self):
        """Test registering a new rule."""

        class TestRule(SEORule):
            name = "Test Rule"
            description = "Test description"
            category = "test"
            weight = 3

            def check(self, obj):
                return SEOResult(status=SEOStatus.GOOD, message="Test")

        # Rule should auto-register via __init_subclass__
        self.assertEqual(SEORuleRegistry.get_rule_count(), 1)
        rule = SEORuleRegistry.get_rule("Test Rule")
        self.assertIsNotNone(rule)
        self.assertIsInstance(rule, TestRule)

    def test_register_rule_without_name_raises_error(self):
        """Test that registering a rule without name raises ValueError."""
        # Rules with empty name should not auto-register
        # But if we try to manually register, it should fail
        with self.assertRaises(ValueError) as context:

            class BadRule(SEORule):
                name = ""  # Empty name

                def check(self, obj):
                    return SEOResult(status=SEOStatus.GOOD, message="Test")

            SEORuleRegistry.register(BadRule)

        self.assertIn("must have a non-empty name", str(context.exception))

    def test_register_duplicate_name_raises_error(self):
        """Test that registering duplicate rule name raises ValueError."""

        class FirstRule(SEORule):
            name = "Duplicate Name"

            def check(self, obj):
                return SEOResult(status=SEOStatus.GOOD, message="First")

        with self.assertRaises(ValueError) as context:

            class SecondRule(SEORule):
                name = "Duplicate Name"

                def check(self, obj):
                    return SEOResult(status=SEOStatus.GOOD, message="Second")

        self.assertIn("already registered", str(context.exception))

    def test_get_rule_returns_cached_instance(self):
        """Test that get_rule returns the same instance on multiple calls."""

        class TestRule(SEORule):
            name = "Cached Rule"

            def check(self, obj):
                return SEOResult(status=SEOStatus.GOOD, message="Test")

        rule1 = SEORuleRegistry.get_rule("Cached Rule")
        rule2 = SEORuleRegistry.get_rule("Cached Rule")

        self.assertIs(rule1, rule2, "Should return same cached instance")

    def test_get_rule_nonexistent_returns_none(self):
        """Test that getting a non-existent rule returns None."""
        rule = SEORuleRegistry.get_rule("Nonexistent Rule")
        self.assertIsNone(rule)

    def test_get_all_rules(self):
        """Test getting all registered rules."""

        class Rule1(SEORule):
            name = "Rule One"

            def check(self, obj):
                return SEOResult(status=SEOStatus.GOOD, message="Test")

        class Rule2(SEORule):
            name = "Rule Two"

            def check(self, obj):
                return SEOResult(status=SEOStatus.GOOD, message="Test")

        rules = SEORuleRegistry.get_all_rules()
        self.assertEqual(len(rules), 2)
        rule_names = [rule.name for rule in rules]
        self.assertIn("Rule One", rule_names)
        self.assertIn("Rule Two", rule_names)

    def test_get_rules_by_category(self):
        """Test getting rules filtered by category."""

        class CoreRule(SEORule):
            name = "Core Rule"
            category = "core_seo"

            def check(self, obj):
                return SEOResult(status=SEOStatus.GOOD, message="Test")

        class SocialRule(SEORule):
            name = "Social Rule"
            category = "social_media"

            def check(self, obj):
                return SEOResult(status=SEOStatus.GOOD, message="Test")

        core_rules = SEORuleRegistry.get_rules_by_category("core_seo")
        self.assertEqual(len(core_rules), 1)
        self.assertEqual(core_rules[0].name, "Core Rule")

        social_rules = SEORuleRegistry.get_rules_by_category("social_media")
        self.assertEqual(len(social_rules), 1)
        self.assertEqual(social_rules[0].name, "Social Rule")

    def test_get_rules_by_nonexistent_category(self):
        """Test getting rules for a category with no rules."""
        rules = SEORuleRegistry.get_rules_by_category("nonexistent")
        self.assertEqual(len(rules), 0)

    def test_get_categories(self):
        """Test getting list of all categories."""

        class Rule1(SEORule):
            name = "Rule 1"
            category = "category_a"

            def check(self, obj):
                return SEOResult(status=SEOStatus.GOOD, message="Test")

        class Rule2(SEORule):
            name = "Rule 2"
            category = "category_b"

            def check(self, obj):
                return SEOResult(status=SEOStatus.GOOD, message="Test")

        categories = SEORuleRegistry.get_categories()
        self.assertEqual(len(categories), 2)
        self.assertIn("category_a", categories)
        self.assertIn("category_b", categories)
        # Should be sorted
        self.assertEqual(categories, sorted(categories))

    def test_get_rule_count(self):
        """Test getting total number of registered rules."""
        self.assertEqual(SEORuleRegistry.get_rule_count(), 0)

        class Rule1(SEORule):
            name = "Rule 1"

            def check(self, obj):
                return SEOResult(status=SEOStatus.GOOD, message="Test")

        self.assertEqual(SEORuleRegistry.get_rule_count(), 1)

        class Rule2(SEORule):
            name = "Rule 2"

            def check(self, obj):
                return SEOResult(status=SEOStatus.GOOD, message="Test")

        self.assertEqual(SEORuleRegistry.get_rule_count(), 2)

    def test_clear_registry(self):
        """Test clearing the registry."""

        class TestRule(SEORule):
            name = "Test Rule"

            def check(self, obj):
                return SEOResult(status=SEOStatus.GOOD, message="Test")

        self.assertEqual(SEORuleRegistry.get_rule_count(), 1)

        SEORuleRegistry.clear()

        self.assertEqual(SEORuleRegistry.get_rule_count(), 0)
        self.assertEqual(len(SEORuleRegistry.get_categories()), 0)


class SEOAuditorTest(SimpleTestCase):
    """Test SEOAuditor functionality."""

    def setUp(self):
        """Set up test rules."""
        SEORuleRegistry.clear()

        class GoodRule(SEORule):
            name = "Good Rule"
            category = "test"
            weight = 3

            def check(self, obj):
                return SEOResult(status=SEOStatus.GOOD, message="Everything is good", score=10)

        class WarningRule(SEORule):
            name = "Warning Rule"
            category = "test"
            weight = 2

            def check(self, obj):
                return SEOResult(status=SEOStatus.WARNING, message="Could be better", score=7)

        self.test_obj = object()

    def tearDown(self):
        """Clean up after tests."""
        SEORuleRegistry.clear()
        import django_seo_audit.rules  # noqa: F401

    def test_auditor_initialization_no_filter(self):
        """Test auditor initialization without category filter."""
        auditor = SEOAuditor()
        self.assertIsNone(auditor.categories)
        self.assertEqual(len(auditor.rules), 2)  # Both rules

    def test_auditor_initialization_with_category_filter(self):
        """Test auditor initialization with category filter."""
        auditor = SEOAuditor(categories=["test"])
        self.assertEqual(auditor.categories, ["test"])
        self.assertEqual(len(auditor.rules), 2)

    def test_auditor_with_nonexistent_category(self):
        """Test auditor with category that has no rules."""
        auditor = SEOAuditor(categories=["nonexistent"])
        self.assertEqual(len(auditor.rules), 0)

    def test_audit_object_returns_result(self):
        """Test that audit_object returns SEOAuditResult."""
        auditor = SEOAuditor()
        result = auditor.audit_object(self.test_obj)
        self.assertIsInstance(result, SEOAuditResult)

    def test_audit_object_runs_all_rules(self):
        """Test that audit_object runs all applicable rules."""
        auditor = SEOAuditor()
        result = auditor.audit_object(self.test_obj)

        # Should have results for both rules
        self.assertEqual(len(result.results), 2)
        self.assertIn("Good Rule", result.results)
        self.assertIn("Warning Rule", result.results)

    def test_audit_object_with_failing_rule(self):
        """Test that one failing rule doesn't break the entire audit."""

        class FailingRule(SEORule):
            name = "Failing Rule"
            category = "test"

            def check(self, obj):
                raise ValueError("This rule fails")

        auditor = SEOAuditor()
        result = auditor.audit_object(self.test_obj)

        # Should still have results, with error result for failing rule
        self.assertIn("Failing Rule", result.results)
        failing_result = result.results["Failing Rule"]
        self.assertEqual(failing_result.status, SEOStatus.CRITICAL)
        self.assertIn("Rule execution failed", failing_result.message)
        self.assertEqual(failing_result.score, 0)

    def test_audit_object_respects_is_applicable_to(self):
        """Test that rules can opt out via is_applicable_to."""

        class SelectiveRule(SEORule):
            name = "Selective Rule"
            category = "test"

            def check(self, obj):
                return SEOResult(status=SEOStatus.GOOD, message="Test")

            def is_applicable_to(self, obj):
                return False  # Never applicable

        auditor = SEOAuditor()
        result = auditor.audit_object(self.test_obj)

        # Selective rule should not appear in results
        self.assertNotIn("Selective Rule", result.results)


class SEOAuditResultTest(SimpleTestCase):
    """Test SEOAuditResult functionality."""

    def test_result_initialization(self):
        """Test creating an audit result."""
        results = {
            "Rule 1": SEOResult(status=SEOStatus.GOOD, message="Good", score=10),
            "Rule 2": SEOResult(status=SEOStatus.WARNING, message="Warning", score=7),
        }
        audit_result = SEOAuditResult(results)

        self.assertEqual(audit_result.results, results)
        self.assertEqual(audit_result.total_rules, 2)

    def test_summary_calculation(self):
        """Test that summary statistics are calculated correctly."""
        results = {
            "Rule 1": SEOResult(status=SEOStatus.GOOD, message="Good", score=10),
            "Rule 2": SEOResult(status=SEOStatus.GOOD, message="Good", score=10),
            "Rule 3": SEOResult(status=SEOStatus.WARNING, message="Warning", score=7),
            "Rule 4": SEOResult(status=SEOStatus.CRITICAL, message="Critical", score=3),
        }
        audit_result = SEOAuditResult(results)

        self.assertEqual(audit_result.total_rules, 4)
        self.assertEqual(audit_result.good_count, 2)
        self.assertEqual(audit_result.warning_count, 1)
        self.assertEqual(audit_result.critical_count, 1)

    def test_overall_score_calculation(self):
        """Test overall score calculation."""
        results = {
            "Rule 1": SEOResult(status=SEOStatus.GOOD, message="Good", score=10),
            "Rule 2": SEOResult(status=SEOStatus.GOOD, message="Good", score=10),
        }
        audit_result = SEOAuditResult(results)

        # (10 + 10) / (2 * 10) * 10 = 10.0
        self.assertEqual(audit_result.overall_score, 10.0)

    def test_overall_score_with_mixed_results(self):
        """Test overall score with mixed results."""
        results = {
            "Rule 1": SEOResult(status=SEOStatus.GOOD, message="Good", score=10),
            "Rule 2": SEOResult(status=SEOStatus.WARNING, message="Warning", score=5),
        }
        audit_result = SEOAuditResult(results)

        # (10 + 5) / (2 * 10) * 10 = 7.5
        self.assertEqual(audit_result.overall_score, 7.5)

    def test_overall_score_empty_results(self):
        """Test overall score with no results."""
        audit_result = SEOAuditResult({})
        self.assertEqual(audit_result.overall_score, 0.0)

    def test_get_results_by_status(self):
        """Test filtering results by status."""
        results = {
            "Rule 1": SEOResult(status=SEOStatus.GOOD, message="Good", score=10),
            "Rule 2": SEOResult(status=SEOStatus.WARNING, message="Warning", score=7),
            "Rule 3": SEOResult(status=SEOStatus.CRITICAL, message="Critical", score=3),
        }
        audit_result = SEOAuditResult(results)

        good_results = audit_result.get_results_by_status(SEOStatus.GOOD)
        self.assertEqual(len(good_results), 1)
        self.assertIn("Rule 1", good_results)

        warning_results = audit_result.get_results_by_status(SEOStatus.WARNING)
        self.assertEqual(len(warning_results), 1)
        self.assertIn("Rule 2", warning_results)

        critical_results = audit_result.get_results_by_status(SEOStatus.CRITICAL)
        self.assertEqual(len(critical_results), 1)
        self.assertIn("Rule 3", critical_results)

    def test_get_critical_issues(self):
        """Test getting critical issues."""
        results = {
            "Rule 1": SEOResult(status=SEOStatus.GOOD, message="Good", score=10),
            "Rule 2": SEOResult(status=SEOStatus.CRITICAL, message="Critical", score=3),
        }
        audit_result = SEOAuditResult(results)

        critical = audit_result.get_critical_issues()
        self.assertEqual(len(critical), 1)
        self.assertIn("Rule 2", critical)

    def test_get_warnings(self):
        """Test getting warnings."""
        results = {
            "Rule 1": SEOResult(status=SEOStatus.GOOD, message="Good", score=10),
            "Rule 2": SEOResult(status=SEOStatus.WARNING, message="Warning", score=7),
        }
        audit_result = SEOAuditResult(results)

        warnings = audit_result.get_warnings()
        self.assertEqual(len(warnings), 1)
        self.assertIn("Rule 2", warnings)

    def test_get_successes(self):
        """Test getting successes."""
        results = {
            "Rule 1": SEOResult(status=SEOStatus.GOOD, message="Good", score=10),
            "Rule 2": SEOResult(status=SEOStatus.WARNING, message="Warning", score=7),
        }
        audit_result = SEOAuditResult(results)

        successes = audit_result.get_successes()
        self.assertEqual(len(successes), 1)
        self.assertIn("Rule 1", successes)

    def test_is_passing_with_no_critical(self):
        """Test is_passing returns True when no critical issues."""
        results = {
            "Rule 1": SEOResult(status=SEOStatus.GOOD, message="Good", score=10),
            "Rule 2": SEOResult(status=SEOStatus.WARNING, message="Warning", score=7),
        }
        audit_result = SEOAuditResult(results)
        self.assertTrue(audit_result.is_passing())

    def test_is_passing_with_critical(self):
        """Test is_passing returns False when critical issues exist."""
        results = {
            "Rule 1": SEOResult(status=SEOStatus.GOOD, message="Good", score=10),
            "Rule 2": SEOResult(status=SEOStatus.CRITICAL, message="Critical", score=3),
        }
        audit_result = SEOAuditResult(results)
        self.assertFalse(audit_result.is_passing())

    def test_get_health_grade_a(self):
        """Test health grade A for score >= 9."""
        results = {"Rule": SEOResult(status=SEOStatus.GOOD, message="Good", score=9)}
        audit_result = SEOAuditResult(results)
        self.assertEqual(audit_result.get_health_grade(), "A")

    def test_get_health_grade_b(self):
        """Test health grade B for score >= 8."""
        results = {"Rule": SEOResult(status=SEOStatus.GOOD, message="Good", score=8)}
        audit_result = SEOAuditResult(results)
        self.assertEqual(audit_result.get_health_grade(), "B")

    def test_get_health_grade_c(self):
        """Test health grade C for score >= 7."""
        results = {"Rule": SEOResult(status=SEOStatus.WARNING, message="Warning", score=7)}
        audit_result = SEOAuditResult(results)
        self.assertEqual(audit_result.get_health_grade(), "C")

    def test_get_health_grade_d(self):
        """Test health grade D for score >= 6."""
        results = {"Rule": SEOResult(status=SEOStatus.WARNING, message="Warning", score=6)}
        audit_result = SEOAuditResult(results)
        self.assertEqual(audit_result.get_health_grade(), "D")

    def test_get_health_grade_f(self):
        """Test health grade F for score < 6."""
        results = {"Rule": SEOResult(status=SEOStatus.CRITICAL, message="Critical", score=5)}
        audit_result = SEOAuditResult(results)
        self.assertEqual(audit_result.get_health_grade(), "F")

    def test_get_summary_text(self):
        """Test summary text generation."""
        results = {
            "Rule 1": SEOResult(status=SEOStatus.GOOD, message="Good", score=10),
            "Rule 2": SEOResult(status=SEOStatus.WARNING, message="Warning", score=7),
            "Rule 3": SEOResult(status=SEOStatus.CRITICAL, message="Critical", score=3),
        }
        audit_result = SEOAuditResult(results)

        summary = audit_result.get_summary_text()
        self.assertIn("SEO Score:", summary)
        self.assertIn("Grade:", summary)
        self.assertIn("1 Good", summary)
        self.assertIn("1 Warnings", summary)
        self.assertIn("1 Critical", summary)
