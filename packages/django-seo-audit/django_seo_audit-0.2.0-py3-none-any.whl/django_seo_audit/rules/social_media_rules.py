"""Social media SEO rules for OpenGraph and Twitter Card optimization.

These rules ensure proper social media sharing optimization through
OpenGraph meta tags and Twitter Card specifications.
"""

from ..core import SEOResult, SEORule, SEOStatus
from ..protocols import SocialMediaAuditable


class OpenGraphImageRule(SEORule):
    """Check if OpenGraph image is properly configured."""

    name = "OpenGraph Image"
    description = "Ensures OpenGraph image is present for social media sharing"
    category = "social_media"
    weight = 3

    def check(self, obj: SocialMediaAuditable) -> SEOResult:
        og_image_url = obj.get_og_image_url()

        if not og_image_url:
            return SEOResult(
                status=SEOStatus.WARNING,
                message="No OpenGraph image set",
                details="Social shares will use default or no image",
                score=4,
                suggestions=[
                    "Add a 1200x630px image for optimal display",
                    "Include relevant visual content",
                    "Ensure image represents the content well",
                ],
            )

        return SEOResult(
            status=SEOStatus.GOOD,
            message="OpenGraph image configured",
            details="Social media sharing optimized",
            score=10,
        )


class OpenGraphTitleRule(SEORule):
    """Check if OpenGraph title is optimized for social sharing."""

    name = "OpenGraph Title"
    description = "Ensures OpenGraph title is engaging for social media"
    category = "social_media"
    weight = 3

    def check(self, obj: SocialMediaAuditable) -> SEOResult:
        og_title = obj.get_og_title().strip()

        if not og_title:
            return SEOResult(
                status=SEOStatus.WARNING,
                message="Using SEO title for OpenGraph",
                details="Consider a more social-friendly title",
                score=6,
                suggestions=[
                    "Create a custom OpenGraph title",
                    "Make it more engaging and shareable",
                    "Can be more conversational than SEO title",
                ],
            )

        length = len(og_title)

        # OpenGraph titles can be up to 95 characters
        if length > 95:
            return SEOResult(
                status=SEOStatus.WARNING,
                message=f"OpenGraph title too long ({length}/95 chars)",
                details="May be truncated on some platforms",
                score=5,
                suggestions=["Shorten to under 95 characters", "Focus on most compelling part"],
            )
        if length < 30:
            return SEOResult(
                status=SEOStatus.WARNING,
                message=f"OpenGraph title short ({length}/30-95 chars)",
                details="Missing opportunity for engagement",
                score=7,
                suggestions=["Add more detail to make it compelling"],
            )

        return SEOResult(status=SEOStatus.GOOD, message=f"OpenGraph title optimized ({length} chars)", score=10)


class OpenGraphDescriptionRule(SEORule):
    """Check if OpenGraph description is optimized for social sharing."""

    name = "OpenGraph Description"
    description = "Ensures OpenGraph description is engaging and informative"
    category = "social_media"
    weight = 2

    def check(self, obj: SocialMediaAuditable) -> SEOResult:
        og_description = obj.get_og_description().strip()

        if not og_description:
            return SEOResult(
                status=SEOStatus.WARNING,
                message="Using meta description for OpenGraph",
                details="Consider a more social-friendly description",
                score=6,
                suggestions=[
                    "Create custom OpenGraph description",
                    "Make it more engaging for social media",
                    "Focus on benefits and intrigue",
                ],
            )

        length = len(og_description)

        # OpenGraph descriptions can be up to 200 characters
        if length > 200:
            return SEOResult(
                status=SEOStatus.WARNING,
                message=f"OpenGraph description too long ({length}/200 chars)",
                details="May be truncated on social platforms",
                score=5,
                suggestions=["Shorten to under 200 characters"],
            )
        if length < 100:
            return SEOResult(
                status=SEOStatus.WARNING,
                message=f"OpenGraph description short ({length}/100-200 chars)",
                details="Could be more descriptive",
                score=7,
                suggestions=["Add more compelling details"],
            )

        return SEOResult(status=SEOStatus.GOOD, message=f"OpenGraph description optimized ({length} chars)", score=10)


class TwitterCardImageRule(SEORule):
    """Check if Twitter Card image is properly configured."""

    name = "Twitter Card Image"
    description = "Ensures Twitter Card has optimized image for sharing"
    category = "social_media"
    weight = 2

    def check(self, obj: SocialMediaAuditable) -> SEOResult:
        twitter_image_url = obj.get_twitter_image_url()
        og_image_url = obj.get_og_image_url()

        if twitter_image_url:
            return SEOResult(
                status=SEOStatus.GOOD,
                message="Dedicated Twitter Card image set",
                details="Optimized for Twitter's format",
                score=10,
            )
        if og_image_url:
            return SEOResult(
                status=SEOStatus.WARNING,
                message="Using OpenGraph image for Twitter",
                details="Consider a Twitter-specific image",
                score=7,
                suggestions=["Add a Twitter-optimized image", "Consider 1200x600px for summary_large_image"],
            )
        return SEOResult(
            status=SEOStatus.WARNING,
            message="No Twitter Card image",
            details="Twitter shares will use default",
            score=4,
            suggestions=["Add a Twitter Card image", "Use 1200x600px for best results", "Ensure image is engaging"],
        )


class TwitterCardTitleRule(SEORule):
    """Check if Twitter Card title is optimized."""

    name = "Twitter Card Title"
    description = "Ensures Twitter Card title is engaging for Twitter users"
    category = "social_media"
    weight = 2

    def check(self, obj: SocialMediaAuditable) -> SEOResult:
        twitter_title = obj.get_twitter_title().strip()

        if not twitter_title:
            return SEOResult(
                status=SEOStatus.WARNING,
                message="Using fallback title for Twitter",
                details="Consider a Twitter-specific title",
                score=6,
                suggestions=[
                    "Create a Twitter-optimized title",
                    "Make it Tweet-friendly",
                    "Consider Twitter's audience and tone",
                ],
            )

        length = len(twitter_title)

        # Twitter titles should be under 70 characters
        if length > 70:
            return SEOResult(
                status=SEOStatus.WARNING,
                message=f"Twitter title too long ({length}/70 chars)",
                details="May be truncated",
                score=5,
                suggestions=["Shorten to under 70 characters"],
            )
        if length < 25:
            return SEOResult(
                status=SEOStatus.WARNING,
                message=f"Twitter title short ({length}/25-70 chars)",
                details="Could be more descriptive",
                score=7,
                suggestions=["Add more engaging details"],
            )

        return SEOResult(status=SEOStatus.GOOD, message=f"Twitter title optimized ({length} chars)", score=10)
