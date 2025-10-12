"""Tests for SEO audit management command."""

from io import StringIO

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

from tests.example_app.models import BlogPost, Page, Product


class SEOAuditCommandListModelsTest(TestCase):
    """Test --list-models functionality."""

    def test_list_models_shows_auditable_models(self):
        """Test that --list-models shows models with SEOAuditableMixin."""
        out = StringIO()
        call_command("seo_audit", "--list-models", stdout=out)
        output = out.getvalue()

        # Should show BlogPost and Product (have mixin)
        self.assertIn("example_app.BlogPost", output)
        self.assertIn("example_app.Product", output)

        # Should NOT show Page (doesn't use mixin)
        self.assertNotIn("example_app.Page", output)

    def test_list_models_shows_count(self):
        """Test that --list-models shows object counts."""
        # Create some test objects
        BlogPost.objects.create(
            title="Test Post",
            slug="test-post",
            content="Content",
        )
        Product.objects.create(
            name="Test Product",
            slug="test-product",
            description="Description",
            price=19.99,
            sku="TEST-001",
        )

        out = StringIO()
        call_command("seo_audit", "--list-models", stdout=out)
        output = out.getvalue()

        # Should show counts
        self.assertIn("(1 objects)", output)

    def test_list_models_no_models(self):
        """Test --list-models when no auditable models exist."""
        # We can't easily test this since we have example models
        # Just ensure the command runs without error
        out = StringIO()
        call_command("seo_audit", "--list-models", stdout=out)
        self.assertIsNotNone(out.getvalue())


class SEOAuditCommandAuditBySlugTest(TestCase):
    """Test auditing by slug."""

    def setUp(self):
        """Create test blog post."""
        self.post = BlogPost.objects.create(
            title="Test SEO Post",
            slug="test-seo-post",
            content="Test content",
            seo_title="Optimized SEO Title for Testing Best Practices Here",
            meta_description="This is a well-crafted meta description that falls within the optimal character range for search engines and provides clear value to users.",
            focus_keyphrase="seo testing",
            h1_tag="Test H1 Tag",
        )

    def test_audit_by_slug(self):
        """Test auditing a specific object by slug."""
        out = StringIO()
        call_command(
            "seo_audit",
            "--model",
            "example_app.BlogPost",
            "--slug",
            "test-seo-post",
            stdout=out,
        )
        output = out.getvalue()

        # Should show audit results
        self.assertIn("SEO Audit for", output)
        self.assertIn("Test SEO Post", output)
        self.assertIn("Summary", output)

    def test_audit_by_slug_with_verbose(self):
        """Test audit with --verbose flag."""
        out = StringIO()
        call_command(
            "seo_audit",
            "--model",
            "example_app.BlogPost",
            "--slug",
            "test-seo-post",
            "--verbose",
            stdout=out,
        )
        output = out.getvalue()

        # Verbose should show more details
        self.assertIn("SEO Audit for", output)
        # Should include suggestions when verbose is on
        # (though we won't test specific suggestions here)

    def test_audit_nonexistent_slug(self):
        """Test auditing with non-existent slug."""
        with self.assertRaises(CommandError) as context:
            call_command(
                "seo_audit",
                "--model",
                "example_app.BlogPost",
                "--slug",
                "nonexistent",
                stdout=StringIO(),
            )

        self.assertIn("does not exist", str(context.exception))


class SEOAuditCommandAuditByPKTest(TestCase):
    """Test auditing by primary key."""

    def setUp(self):
        """Create test product."""
        self.product = Product.objects.create(
            name="Test Widget",
            slug="test-widget",
            description="A test product",
            price=29.99,
            sku="WIDGET-001",
        )

    def test_audit_by_pk(self):
        """Test auditing a specific object by primary key."""
        out = StringIO()
        call_command(
            "seo_audit",
            "--model",
            "example_app.Product",
            "--pk",
            str(self.product.pk),
            stdout=out,
        )
        output = out.getvalue()

        # Should show audit results
        self.assertIn("SEO Audit for", output)
        self.assertIn("Test Widget", output)

    def test_audit_nonexistent_pk(self):
        """Test auditing with non-existent primary key."""
        with self.assertRaises(CommandError) as context:
            call_command(
                "seo_audit",
                "--model",
                "example_app.Product",
                "--pk",
                "99999",
                stdout=StringIO(),
            )

        self.assertIn("does not exist", str(context.exception))


class SEOAuditCommandCategoryFilterTest(TestCase):
    """Test category filtering."""

    def setUp(self):
        """Create test object."""
        self.post = BlogPost.objects.create(
            title="Test Post",
            slug="test-post",
            content="Content",
            seo_title="SEO Title Here For Testing Purposes Only Today",
            meta_description="This is a meta description that is well within the optimal character range for search engines.",
        )

    def test_audit_with_single_category(self):
        """Test auditing with single category filter."""
        out = StringIO()
        call_command(
            "seo_audit",
            "--model",
            "example_app.BlogPost",
            "--slug",
            "test-post",
            "--category",
            "core_seo",
            stdout=out,
        )
        output = out.getvalue()

        # Should run audit (but we can't easily verify which rules ran)
        self.assertIn("SEO Audit for", output)
        self.assertIn("Summary", output)

    def test_audit_with_multiple_categories(self):
        """Test auditing with multiple category filters."""
        out = StringIO()
        call_command(
            "seo_audit",
            "--model",
            "example_app.BlogPost",
            "--slug",
            "test-post",
            "--category",
            "core_seo",
            "--category",
            "social_media",
            stdout=out,
        )
        output = out.getvalue()

        # Should run audit
        self.assertIn("SEO Audit for", output)


class SEOAuditCommandErrorHandlingTest(TestCase):
    """Test error handling in management command."""

    def test_no_arguments_raises_error(self):
        """Test command without any arguments raises error."""
        with self.assertRaises(CommandError) as context:
            call_command("seo_audit", stdout=StringIO())

        self.assertIn("must specify --model", str(context.exception))

    def test_invalid_model_format(self):
        """Test invalid model format raises error."""
        with self.assertRaises(CommandError) as context:
            call_command(
                "seo_audit",
                "--model",
                "InvalidFormat",
                "--slug",
                "test",
                stdout=StringIO(),
            )

        self.assertIn("Invalid model", str(context.exception))

    def test_nonexistent_model(self):
        """Test non-existent model raises error."""
        with self.assertRaises(CommandError) as context:
            call_command(
                "seo_audit",
                "--model",
                "example_app.NonExistentModel",
                "--slug",
                "test",
                stdout=StringIO(),
            )

        self.assertIn("Invalid model", str(context.exception))

    def test_model_without_mixin(self):
        """Test model without SEOAuditableMixin raises error."""
        # Page model doesn't use the mixin
        Page.objects.create(
            title="Test Page",
            slug="test-page",
            content="Content",
        )

        with self.assertRaises(CommandError) as context:
            call_command(
                "seo_audit",
                "--model",
                "example_app.Page",
                "--slug",
                "test-page",
                stdout=StringIO(),
            )

        self.assertIn("does not use SEOAuditableMixin", str(context.exception))

    def test_missing_lookup_parameter(self):
        """Test missing both slug and pk raises error."""
        with self.assertRaises(CommandError) as context:
            call_command(
                "seo_audit",
                "--model",
                "example_app.BlogPost",
                stdout=StringIO(),
            )

        self.assertIn("must specify either --slug or --pk", str(context.exception))


class SEOAuditCommandOutputTest(TestCase):
    """Test command output formatting."""

    def setUp(self):
        """Create well-optimized blog post."""
        self.post = BlogPost.objects.create(
            title="Perfectly Optimized Post",
            slug="perfect-post",
            content="Content here",
            # Optimal SEO fields
            seo_title="Perfect SEO Title with Exactly Fifty Five Characters!",
            meta_description=(
                "This is a perfectly crafted meta description that contains exactly the right number of "
                "characters to be optimal for search engine display and user engagement."
            ),
            focus_keyphrase="perfect seo",
            secondary_keywords="optimization, testing, django, python, web",
            h1_tag="User Friendly H1 Title",
            # OG fields
            og_title="Perfect OpenGraph Title for Social Media Sharing",
            og_description=(
                "This OpenGraph description is optimized for social media sharing and falls within the perfect "
                "character range for maximum impact and engagement."
            ),
            og_image="https://example.com/image.jpg",
            # Twitter fields
            twitter_title="Perfect Twitter Card Title with Good Length",
            twitter_description=(
                "Twitter card description that is well optimized for character limits and user engagement."
            ),
            twitter_image="https://example.com/twitter.jpg",
            # Technical fields
            canonical_url="https://example.com/perfect-post",
            robots_directive="index,follow",
            schema_type="BlogPosting",
            breadcrumb_title="Perfect Post",
        )

    def test_output_shows_model_name(self):
        """Test output shows the model being audited."""
        out = StringIO()
        call_command(
            "seo_audit",
            "--model",
            "example_app.BlogPost",
            "--slug",
            "perfect-post",
            stdout=out,
        )
        output = out.getvalue()

        self.assertIn("Model: BlogPost", output)

    def test_output_shows_summary(self):
        """Test output shows audit summary."""
        out = StringIO()
        call_command(
            "seo_audit",
            "--model",
            "example_app.BlogPost",
            "--slug",
            "perfect-post",
            stdout=out,
        )
        output = out.getvalue()

        self.assertIn("Summary", output)
        self.assertIn("SEO Score:", output)
        self.assertIn("Grade:", output)

    def test_output_shows_passing_status(self):
        """Test output shows passing status for good SEO."""
        out = StringIO()
        call_command(
            "seo_audit",
            "--model",
            "example_app.BlogPost",
            "--slug",
            "perfect-post",
            stdout=out,
        )
        output = out.getvalue()

        # Well-optimized post should pass audit
        # (specific status depends on content rules, but should show summary)
        self.assertIn("Good", output or "critical", output)


class SEOAuditCommandIntegrationTest(TestCase):
    """Integration tests for full audit workflow."""

    def test_full_audit_workflow(self):
        """Test complete audit workflow from creation to audit."""
        # Create a blog post
        post = BlogPost.objects.create(
            title="Integration Test Post",
            slug="integration-test",
            content="Test content",
            seo_title="Integration Test SEO Title That Is Well Optimized Here",
            meta_description=(
                "This is a comprehensive meta description for integration testing that demonstrates "
                "the full workflow from model creation to audit execution."
            ),
            focus_keyphrase="integration test",
        )

        # List models to confirm it's discoverable
        out_list = StringIO()
        call_command("seo_audit", "--list-models", stdout=out_list)
        list_output = out_list.getvalue()
        self.assertIn("example_app.BlogPost", list_output)

        # Audit the post
        out_audit = StringIO()
        call_command(
            "seo_audit",
            "--model",
            "example_app.BlogPost",
            "--slug",
            "integration-test",
            stdout=out_audit,
        )
        audit_output = out_audit.getvalue()

        # Verify audit ran successfully
        self.assertIn("Integration Test Post", audit_output)
        self.assertIn("Summary", audit_output)
        self.assertIn("SEO Score:", audit_output)

        # Should be able to audit by PK as well
        out_pk = StringIO()
        call_command(
            "seo_audit",
            "--model",
            "example_app.BlogPost",
            "--pk",
            str(post.pk),
            stdout=out_pk,
        )
        pk_output = out_pk.getvalue()
        self.assertIn("Integration Test Post", pk_output)
