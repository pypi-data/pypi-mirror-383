"""Content quality and completeness SEO rules.

These rules assess the quality, depth, and completeness of content
which are important factors for SEO success and user engagement.
"""

from ..core import SEOResult, SEORule, SEOStatus
from ..protocols import ContentAuditable


class DetailedContentRule(SEORule):
    """Check if category has detailed content beyond basic fields."""

    name = "Detailed Content"
    description = "Ensures category has comprehensive content for better SEO"
    category = "content"
    weight = 5

    def check(self, obj: ContentAuditable) -> SEOResult:
        has_content = obj.has_detailed_content()

        if not has_content:
            return SEOResult(
                status=SEOStatus.CRITICAL,
                message="No detailed content found",
                details="Missing comprehensive content sections",
                score=0,
                suggestions=[
                    "Create CategorySubpages with comprehensive content",
                    "Add introduction, how-it-works, requirements, and tips sections",
                    "Provide valuable, in-depth information",
                ],
            )

        sections_count = obj.get_content_sections_count()
        word_count = obj.get_content_word_count()

        if sections_count >= 5 and word_count >= 500:
            return SEOResult(
                status=SEOStatus.GOOD,
                message=f"Comprehensive content ({sections_count} sections, {word_count} words)",
                score=10,
            )
        if sections_count >= 3 and word_count >= 300:
            return SEOResult(
                status=SEOStatus.WARNING,
                message=f"Good content ({sections_count} sections, {word_count} words)",
                details="Could be more comprehensive",
                score=7,
                suggestions=[
                    "Add more content sections",
                    "Expand existing sections with more detail",
                    "Aim for 500+ words total",
                ],
            )
        return SEOResult(
            status=SEOStatus.CRITICAL,
            message=f"Limited content ({sections_count} sections, {word_count} words)",
            details="Insufficient depth for good SEO",
            score=3,
            suggestions=[
                "Add more comprehensive content",
                "Create multiple detailed sections",
                "Aim for at least 5 sections and 500 words",
            ],
        )


class IntroductionContentRule(SEORule):
    """Check if category has a proper introduction section."""

    name = "Introduction Content"
    description = "Ensures category has an engaging introduction for users and search engines"
    category = "content"
    weight = 3

    def check(self, obj: ContentAuditable) -> SEOResult:
        has_intro = obj.has_introduction_content()

        if not has_intro:
            return SEOResult(
                status=SEOStatus.CRITICAL,
                message="No introduction content",
                details="Missing critical first impression content",
                score=0,
                suggestions=[
                    "Write a compelling introduction",
                    "Explain what the category is about",
                    "Hook readers from the start",
                ],
            )

        return SEOResult(
            status=SEOStatus.GOOD,
            message="Introduction content present",
            details="Good foundation for user engagement",
            score=10,
        )


class ResourceCountRule(SEORule):
    """Check if category has sufficient supporting resources."""

    name = "Supporting Resources"
    description = "Ensures category has helpful resources like videos, articles, and tools"
    category = "content"
    weight = 3

    def check(self, obj: ContentAuditable) -> SEOResult:
        total_resources = obj.get_resource_count()
        featured_resources = obj.get_featured_resource_count()

        if total_resources == 0:
            return SEOResult(
                status=SEOStatus.WARNING,
                message="No supporting resources",
                details="Missing helpful external content",
                score=4,
                suggestions=[
                    "Add relevant videos, articles, or tools",
                    "Include high-quality external resources",
                    "Feature the most valuable resources",
                ],
            )
        if total_resources < 3:
            return SEOResult(
                status=SEOStatus.WARNING,
                message=f"Few resources ({total_resources})",
                details="Could benefit from more supporting content",
                score=6,
                suggestions=["Add more relevant resources", "Include variety: videos, articles, tools"],
            )
        if featured_resources == 0:
            return SEOResult(
                status=SEOStatus.WARNING,
                message=f"Resources available ({total_resources}) but none featured",
                details="Consider highlighting best resources",
                score=7,
                suggestions=["Feature 2-3 most valuable resources", "Highlight quality over quantity"],
            )
        return SEOResult(
            status=SEOStatus.GOOD,
            message=f"Good resources ({total_resources} total, {featured_resources} featured)",
            score=10,
        )


class ContentDepthRule(SEORule):
    """Evaluate overall content depth and quality."""

    name = "Content Depth"
    description = "Assesses content comprehensiveness for SEO value"
    category = "content"
    weight = 4

    def check(self, obj: ContentAuditable) -> SEOResult:
        word_count = obj.get_content_word_count()
        sections_count = obj.get_content_sections_count()

        if word_count == 0:
            return SEOResult(
                status=SEOStatus.CRITICAL,
                message="No content found",
                score=0,
                suggestions=["Create comprehensive content"],
            )

        # Calculate content quality score
        if word_count >= 800 and sections_count >= 6:
            return SEOResult(
                status=SEOStatus.GOOD,
                message=f"Excellent content depth ({word_count} words, {sections_count} sections)",
                details="Comprehensive coverage of topic",
                score=10,
            )
        if word_count >= 500 and sections_count >= 4:
            return SEOResult(
                status=SEOStatus.GOOD,
                message=f"Good content depth ({word_count} words, {sections_count} sections)",
                score=8,
            )
        if word_count >= 300 and sections_count >= 3:
            return SEOResult(
                status=SEOStatus.WARNING,
                message=f"Moderate content depth ({word_count} words, {sections_count} sections)",
                details="Good foundation but could be expanded",
                score=6,
                suggestions=[
                    "Expand content to 500+ words",
                    "Add more detailed sections",
                    "Include practical examples and tips",
                ],
            )
        return SEOResult(
            status=SEOStatus.CRITICAL,
            message=f"Shallow content ({word_count} words, {sections_count} sections)",
            details="Insufficient for good SEO performance",
            score=3,
            suggestions=[
                "Create comprehensive content (800+ words)",
                "Add multiple detailed sections",
                "Provide real value to readers",
            ],
        )
