"""Rule registry and audit orchestration system.

This module provides the central registry for SEO rules and the main
auditor class that coordinates running all registered rules against
auditable objects.
"""

from collections import defaultdict
from typing import Any

from .core import SEOResult, SEORule, SEOStatus


class SEORuleRegistry:
    """Central registry for all SEO audit rules.

    This registry automatically discovers and organizes rules as they're
    defined, providing lookup capabilities by category and enabling
    the auditor to run all applicable rules.
    """

    _rules: dict[str, type[SEORule]] = {}
    _categories: dict[str, list[type[SEORule]]] = defaultdict(list)
    _instances: dict[str, SEORule] = {}  # Cached rule instances

    @classmethod
    def register(cls, rule_class: type[SEORule]) -> None:
        """Register a new SEO rule class.

        Args:
            rule_class: The SEORule subclass to register

        Raises:
            ValueError: If rule name already exists or is empty

        """
        if not rule_class.name:
            raise ValueError(f"Rule {rule_class.__name__} must have a non-empty name")

        if rule_class.name in cls._rules:
            existing_class = cls._rules[rule_class.name].__name__
            raise ValueError(f"Rule name '{rule_class.name}' already registered by {existing_class}")

        # Register the rule
        cls._rules[rule_class.name] = rule_class
        cls._categories[rule_class.category].append(rule_class)

        # Clear cached instance if it exists
        if rule_class.name in cls._instances:
            del cls._instances[rule_class.name]

    @classmethod
    def get_rule(cls, name: str) -> SEORule | None:
        """Get a rule instance by name.

        Args:
            name: The rule name to look up

        Returns:
            Rule instance or None if not found

        """
        if name not in cls._rules:
            return None

        # Return cached instance or create new one
        if name not in cls._instances:
            rule_class = cls._rules[name]
            cls._instances[name] = rule_class()

        return cls._instances[name]

    @classmethod
    def get_all_rules(cls) -> list[SEORule]:
        """Get instances of all registered rules.

        Returns:
            List of all rule instances

        """
        return [cls.get_rule(name) for name in cls._rules]

    @classmethod
    def get_rules_by_category(cls, category: str) -> list[SEORule]:
        """Get all rules in a specific category.

        Args:
            category: The category name to filter by

        Returns:
            List of rule instances in the category

        """
        rule_classes = cls._categories.get(category, [])
        return [rule_class() for rule_class in rule_classes]

    @classmethod
    def get_categories(cls) -> list[str]:
        """Get list of all rule categories.

        Returns:
            Sorted list of category names

        """
        return sorted(cls._categories.keys())

    @classmethod
    def get_rule_count(cls) -> int:
        """Get total number of registered rules.

        Returns:
            Number of registered rules

        """
        return len(cls._rules)

    @classmethod
    def clear(cls) -> None:
        """Clear all registered rules (primarily for testing)."""
        cls._rules.clear()
        cls._categories.clear()
        cls._instances.clear()


class SEOAuditor:
    """Main auditor class that coordinates SEO rule execution.

    The auditor runs all applicable rules against an object and aggregates
    the results, providing overall scoring and categorized feedback.
    """

    def __init__(self, categories: list[str] | None = None) -> None:
        """Initialize auditor with optional category filtering.

        Args:
            categories: List of categories to include, or None for all

        """
        self.categories = categories
        self.rules = self._get_applicable_rules()

    def _get_applicable_rules(self) -> list[SEORule]:
        """Get list of rules to run based on category filter."""
        if self.categories is None:
            return SEORuleRegistry.get_all_rules()

        rules = []
        for category in self.categories:
            rules.extend(SEORuleRegistry.get_rules_by_category(category))
        return rules

    def audit_object(self, obj: Any) -> "SEOAuditResult":
        """Run all applicable rules against an object.

        Args:
            obj: Object to audit (should implement relevant protocols)

        Returns:
            SEOAuditResult containing all rule results and summary

        """
        results = {}

        for rule in self.rules:
            try:
                # Check if rule is applicable to this object
                if not rule.is_applicable_to(obj):
                    continue

                result = rule.check(obj)
                results[rule.name] = result

            except Exception as e:
                # Graceful degradation - don't let one rule break the audit
                results[rule.name] = SEOResult(
                    status=SEOStatus.CRITICAL,
                    message=f"Rule execution failed: {e!s}",
                    details=f"Error in {rule.__class__.__name__}",
                    score=0,
                    suggestions=["Check rule implementation for errors"],
                )

        return SEOAuditResult(results)


class SEOAuditResult:
    """Container for complete SEO audit results with analysis methods.

    Provides aggregation, filtering, and summary capabilities for
    audit results from multiple rules.
    """

    def __init__(self, results: dict[str, SEOResult]) -> None:
        """Initialize with rule results dictionary.

        Args:
            results: Dictionary mapping rule names to SEOResult objects

        """
        self.results = results
        self._calculate_summary()

    def _calculate_summary(self) -> None:
        """Calculate summary statistics from results."""
        self.total_rules = len(self.results)
        self.good_count = sum(1 for r in self.results.values() if r.status == SEOStatus.GOOD)
        self.warning_count = sum(1 for r in self.results.values() if r.status == SEOStatus.WARNING)
        self.critical_count = sum(1 for r in self.results.values() if r.status == SEOStatus.CRITICAL)

        # Calculate weighted score (0-10 scale)
        if self.total_rules > 0:
            total_score = sum(result.score for result in self.results.values())
            self.overall_score = round(total_score / (self.total_rules * 10) * 10, 1)
        else:
            self.overall_score = 0.0

    def get_results_by_status(self, status: SEOStatus) -> dict[str, SEOResult]:
        """Get all results with a specific status.

        Args:
            status: The SEOStatus to filter by

        Returns:
            Dictionary of rule names to results with the specified status

        """
        return {name: result for name, result in self.results.items() if result.status == status}

    def get_critical_issues(self) -> dict[str, SEOResult]:
        """Get all critical issues that need immediate attention."""
        return self.get_results_by_status(SEOStatus.CRITICAL)

    def get_warnings(self) -> dict[str, SEOResult]:
        """Get all warnings that could be improved."""
        return self.get_results_by_status(SEOStatus.WARNING)

    def get_successes(self) -> dict[str, SEOResult]:
        """Get all successful checks."""
        return self.get_results_by_status(SEOStatus.GOOD)

    def is_passing(self) -> bool:
        """Return True if audit has no critical issues."""
        return self.critical_count == 0

    def get_health_grade(self) -> str:
        """Get letter grade based on overall score.

        Returns:
            Letter grade (A, B, C, D, F) based on score

        """
        if self.overall_score >= 9:
            return "A"
        if self.overall_score >= 8:
            return "B"
        if self.overall_score >= 7:
            return "C"
        if self.overall_score >= 6:
            return "D"
        return "F"

    def get_summary_text(self) -> str:
        """Get human-readable summary of audit results."""
        grade = self.get_health_grade()
        return (
            f"SEO Score: {self.overall_score}/10 (Grade: {grade})\n"
            f"Results: {self.good_count} Good, {self.warning_count} Warnings, "
            f"{self.critical_count} Critical"
        )
