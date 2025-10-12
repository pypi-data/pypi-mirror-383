"""Core SEO rules for fundamental search engine optimization checks.

These rules focus on the essential SEO elements that every page should have:
title optimization, meta descriptions, keyword usage, and URL structure.
"""

from ..core import SEOResult, SEORule, SEOStatus
from ..protocols import BasicSEOAuditable


class SEOTitleLengthRule(SEORule):
    """Check if SEO title is within optimal length range."""

    name = "SEO Title Length"
    description = "Ensures SEO title is 50-60 characters for optimal search display"
    category = "core_seo"
    weight = 5

    def check(self, obj: BasicSEOAuditable) -> SEOResult:
        title = obj.get_seo_title()
        length = len(title)

        if 50 <= length <= 60:
            return SEOResult(status=SEOStatus.GOOD, message=f"Optimal length ({length} chars)", score=10)
        if 40 <= length < 50:
            return SEOResult(
                status=SEOStatus.WARNING,
                message=f"Could be longer ({length}/50-60 chars)",
                details="Consider adding more descriptive keywords",
                score=7,
                suggestions=["Add more descriptive terms", "Include target keywords"],
            )
        if 60 < length <= 70:
            return SEOResult(
                status=SEOStatus.WARNING,
                message=f"Slightly long ({length}/50-60 chars)",
                details="May be truncated in search results",
                score=6,
                suggestions=["Shorten to under 60 characters", "Remove less important words"],
            )
        return SEOResult(
            status=SEOStatus.CRITICAL,
            message=f"Poor length ({length} chars)",
            details="Too short" if length < 40 else "Will be truncated",
            score=2,
            suggestions=[
                "Rewrite to 50-60 characters" if length < 40 else "Significantly shorten title",
                "Include primary keyword",
                "Make it compelling for users",
            ],
        )


class MetaDescriptionLengthRule(SEORule):
    """Check if meta description is within optimal length range."""

    name = "Meta Description Length"
    description = "Ensures meta description is 150-160 characters for optimal search display"
    category = "core_seo"
    weight = 4

    def check(self, obj: BasicSEOAuditable) -> SEOResult:
        description = obj.get_meta_description()

        if not description or not description.strip():
            return SEOResult(
                status=SEOStatus.CRITICAL,
                message="Meta description is missing",
                details="Search engines will auto-generate snippets",
                score=0,
                suggestions=[
                    "Write a compelling 150-160 character description",
                    "Include primary keyword naturally",
                    "Focus on benefits to users",
                ],
            )

        length = len(description)

        if 150 <= length <= 160:
            return SEOResult(status=SEOStatus.GOOD, message=f"Optimal length ({length} chars)", score=10)
        if 130 <= length < 150:
            return SEOResult(
                status=SEOStatus.WARNING,
                message=f"Could be longer ({length}/150-160 chars)",
                details="Missing opportunity for more compelling copy",
                score=7,
                suggestions=["Add more detail about benefits", "Include call-to-action"],
            )
        if 160 < length <= 180:
            return SEOResult(
                status=SEOStatus.WARNING,
                message=f"Slightly long ({length}/150-160 chars)",
                details="May be truncated in search results",
                score=6,
                suggestions=["Trim to under 160 characters", "Remove less essential words"],
            )
        return SEOResult(
            status=SEOStatus.CRITICAL,
            message=f"Poor length ({length} chars)",
            details="Too short" if length < 130 else "Will be truncated",
            score=2,
            suggestions=[
                "Rewrite to 150-160 characters",
                "Make it compelling and keyword-rich",
                "Focus on unique value proposition",
            ],
        )


class FocusKeyphraseRule(SEORule):
    """Check if focus keyphrase is defined and used appropriately."""

    name = "Focus Keyphrase"
    description = "Ensures primary keyword is defined and used in title and description"
    category = "core_seo"
    weight = 5

    def check(self, obj: BasicSEOAuditable) -> SEOResult:
        keyphrase = obj.get_focus_keyphrase().strip()

        if not keyphrase:
            return SEOResult(
                status=SEOStatus.CRITICAL,
                message="No focus keyphrase defined",
                details="Missing primary SEO target",
                score=0,
                suggestions=[
                    "Research and define a primary keyword",
                    "Choose terms your audience searches for",
                    "Consider search volume and competition",
                ],
            )

        title = obj.get_seo_title().lower()
        description = obj.get_meta_description().lower()
        keyphrase_lower = keyphrase.lower()

        title_has_keyword = keyphrase_lower in title
        desc_has_keyword = keyphrase_lower in description

        if title_has_keyword and desc_has_keyword:
            return SEOResult(
                status=SEOStatus.GOOD,
                message=f"Keyword '{keyphrase}' well-placed",
                details="Present in both title and description",
                score=10,
            )
        if title_has_keyword:
            return SEOResult(
                status=SEOStatus.WARNING,
                message=f"Keyword '{keyphrase}' in title only",
                details="Missing from meta description",
                score=7,
                suggestions=["Include keyword naturally in meta description"],
            )
        if desc_has_keyword:
            return SEOResult(
                status=SEOStatus.WARNING,
                message=f"Keyword '{keyphrase}' in description only",
                details="Missing from title",
                score=6,
                suggestions=["Include keyword in SEO title", "Consider title rewrite"],
            )
        return SEOResult(
            status=SEOStatus.CRITICAL,
            message=f"Keyword '{keyphrase}' not found",
            details="Missing from both title and description",
            score=2,
            suggestions=[
                "Include keyword in SEO title",
                "Add keyword to meta description",
                "Ensure natural, readable usage",
            ],
        )


class H1TagRule(SEORule):
    """Check if H1 tag is properly optimized."""

    name = "H1 Tag Optimization"
    description = "Ensures H1 tag is present and differs from page title when needed"
    category = "core_seo"
    weight = 3

    def check(self, obj: BasicSEOAuditable) -> SEOResult:
        h1_tag = obj.get_h1_tag().strip()
        seo_title = obj.get_seo_title().strip()

        if not h1_tag:
            return SEOResult(
                status=SEOStatus.CRITICAL,
                message="H1 tag is empty",
                details="Using SEO title as fallback",
                score=0,
                suggestions=[
                    "Set a custom H1 tag",
                    "Make it user-focused rather than SEO-focused",
                    "Can be different from page title",
                ],
            )

        if h1_tag == seo_title:
            return SEOResult(
                status=SEOStatus.WARNING,
                message="H1 identical to SEO title",
                details="Consider making H1 more user-friendly",
                score=6,
                suggestions=[
                    "Make H1 more conversational",
                    "Focus on user benefit rather than keywords",
                    "Keep SEO title keyword-optimized",
                ],
            )

        # Check length - H1 can be longer than title
        length = len(h1_tag)
        if length > 100:
            return SEOResult(
                status=SEOStatus.WARNING,
                message=f"H1 tag is long ({length}/100 chars)",
                details="Consider shortening for better readability",
                score=7,
                suggestions=["Shorten to under 70 characters", "Focus on main benefit"],
            )

        return SEOResult(
            status=SEOStatus.GOOD,
            message="H1 tag well optimized",
            details=f"Unique from title, {length} characters",
            score=10,
        )


class SecondaryKeywordsRule(SEORule):
    """Check if secondary keywords are defined for content depth."""

    name = "Secondary Keywords"
    description = "Ensures secondary keywords are defined to support content strategy"
    category = "core_seo"
    weight = 2

    def check(self, obj: BasicSEOAuditable) -> SEOResult:
        keywords = obj.get_secondary_keywords().strip()

        if not keywords:
            return SEOResult(
                status=SEOStatus.WARNING,
                message="No secondary keywords defined",
                details="Missing opportunity for broader reach",
                score=5,
                suggestions=["Add 3-5 related keywords", "Include long-tail variations", "Consider semantic keywords"],
            )

        # Count keywords (split by comma)
        keyword_list = [k.strip() for k in keywords.split(",") if k.strip()]
        count = len(keyword_list)

        if 3 <= count <= 7:
            return SEOResult(
                status=SEOStatus.GOOD,
                message=f"Good keyword variety ({count} keywords)",
                details=", ".join(keyword_list[:3]) + "..." if count > 3 else ", ".join(keyword_list),
                score=10,
            )
        if 1 <= count < 3:
            return SEOResult(
                status=SEOStatus.WARNING,
                message=f"Few keywords defined ({count})",
                details="Consider adding more variations",
                score=7,
                suggestions=["Add more related terms", "Include long-tail keywords"],
            )
        return SEOResult(
            status=SEOStatus.WARNING,
            message=f"Many keywords ({count})",
            details="May be unfocused",
            score=6,
            suggestions=["Focus on 3-7 most important terms", "Remove less relevant keywords"],
        )
