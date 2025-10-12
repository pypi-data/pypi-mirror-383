"""Technical SEO rules for advanced optimization checks.

These rules focus on technical SEO aspects like structured data,
canonical URLs, robots directives, and other technical elements.
"""

from ..core import SEOResult, SEORule, SEOStatus
from ..protocols import TechnicalSEOAuditable


class CanonicalURLRule(SEORule):
    """Check if canonical URL is properly configured."""

    name = "Canonical URL"
    description = "Ensures canonical URL is set when needed to prevent duplicate content"
    category = "technical_seo"
    weight = 3

    def check(self, obj: TechnicalSEOAuditable) -> SEOResult:
        has_custom_canonical = obj.has_custom_canonical_url()

        if has_custom_canonical:
            return SEOResult(
                status=SEOStatus.GOOD,
                message="Custom canonical URL configured",
                details="Helps prevent duplicate content issues",
                score=10,
            )

        # Default canonical URLs are good - system always provides them
        return SEOResult(
            status=SEOStatus.GOOD,
            message="Default canonical URL configured",
            details="System automatically provides canonical URL via get_absolute_url()",
            score=9,
        )


class RobotsDirectiveRule(SEORule):
    """Check if robots directive is properly configured."""

    name = "Robots Directive"
    description = "Ensures robots meta directive is appropriate for the content"
    category = "technical_seo"
    weight = 2

    def check(self, obj: TechnicalSEOAuditable) -> SEOResult:
        robots = obj.get_robots_directive().lower()

        # Check for problematic directives
        if "noindex" in robots:
            return SEOResult(
                status=SEOStatus.CRITICAL,
                message="Page set to NOINDEX",
                details="Search engines won't index this content",
                score=0,
                suggestions=[
                    "Change to 'index,follow' for public content",
                    "Only use noindex for private/test content",
                ],
            )

        if "nofollow" in robots and "index" in robots:
            return SEOResult(
                status=SEOStatus.WARNING,
                message="Page indexed but links not followed",
                details="May limit SEO value of internal links",
                score=5,
                suggestions=[
                    "Consider 'index,follow' for full SEO benefit",
                    "Use nofollow only when specifically needed",
                ],
            )

        if robots in ["index,follow", "index, follow"]:
            return SEOResult(
                status=SEOStatus.GOOD,
                message="Robots directive optimized",
                details="Allows indexing and link following",
                score=10,
            )

        return SEOResult(
            status=SEOStatus.WARNING,
            message=f"Custom robots directive: {robots}",
            details="Verify this is intentional",
            score=6,
            suggestions=["Ensure directive matches content strategy"],
        )


class StructuredDataRule(SEORule):
    """Check if structured data is properly configured."""

    name = "Structured Data"
    description = "Ensures Schema.org structured data is configured for rich snippets"
    category = "technical_seo"
    weight = 3

    def check(self, obj: TechnicalSEOAuditable) -> SEOResult:
        schema_type = obj.get_schema_type()
        schema_data = obj.get_schema_data()

        if not schema_type or schema_type.lower() == "none":
            return SEOResult(
                status=SEOStatus.WARNING,
                message="No structured data type set",
                details="Missing opportunity for rich snippets",
                score=4,
                suggestions=[
                    "Set appropriate Schema.org type (Article, HowTo, FAQ)",
                    "Add structured data for better search display",
                    "Consider markup for rich snippets",
                ],
            )

        # Check for appropriate schema types
        good_types = ["article", "howto", "faq", "course", "guide"]
        if schema_type.lower() in good_types:
            score = 10 if schema_data else 8
            message = "Good structured data type"
            details = f"Using {schema_type}" + (" with additional data" if schema_data else "")

            return SEOResult(
                status=SEOStatus.GOOD,
                message=message,
                details=details,
                score=score,
                suggestions=["Consider adding more structured data fields"] if not schema_data else None,
            )

        return SEOResult(
            status=SEOStatus.WARNING,
            message=f"Schema type: {schema_type}",
            details="Verify this is the best type for your content",
            score=6,
            suggestions=["Consider Article, HowTo, or FAQ types", "Match schema type to content purpose"],
        )


class BreadcrumbOptimizationRule(SEORule):
    """Check if breadcrumb navigation is optimized."""

    name = "Breadcrumb Optimization"
    description = "Ensures breadcrumb title is user-friendly and SEO-optimized"
    category = "technical_seo"
    weight = 2

    def check(self, obj: TechnicalSEOAuditable) -> SEOResult:
        breadcrumb_title = obj.get_breadcrumb_title()

        # This is a basic check - in a real implementation, you might
        # compare against the actual page title or check length
        if not breadcrumb_title:
            return SEOResult(
                status=SEOStatus.WARNING,
                message="Using default breadcrumb title",
                details="Consider custom breadcrumb for better navigation",
                score=6,
                suggestions=[
                    "Set custom breadcrumb title",
                    "Make it concise and descriptive",
                    "Help users understand their location",
                ],
            )

        length = len(breadcrumb_title)
        if length > 50:
            return SEOResult(
                status=SEOStatus.WARNING,
                message=f"Breadcrumb title long ({length}/50 chars)",
                details="May be truncated in navigation",
                score=6,
                suggestions=["Shorten to under 50 characters"],
            )
        if length < 15:
            return SEOResult(
                status=SEOStatus.WARNING,
                message=f"Breadcrumb title short ({length}/15-50 chars)",
                details="Could be more descriptive",
                score=7,
                suggestions=["Add more descriptive detail"],
            )

        return SEOResult(status=SEOStatus.GOOD, message=f"Breadcrumb optimized ({length} chars)", score=10)
