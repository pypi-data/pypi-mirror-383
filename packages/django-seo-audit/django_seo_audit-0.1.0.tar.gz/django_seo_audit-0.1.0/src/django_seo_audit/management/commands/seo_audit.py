"""SEO audit management command with auto-discovery.

Usage:
    # List all auditable models
    python manage.py seo_audit --list-models

    # Audit specific model instance by slug
    python manage.py seo_audit --model categories.Category --slug web-development

    # Audit by primary key
    python manage.py seo_audit --model pages.Page --pk 42

    # Audit with specific rule categories
    python manage.py seo_audit --model categories.Category --slug test --category core_seo

This command automatically discovers all models using SEOAuditableMixin
and performs comprehensive SEO audits using the protocol-based rule system.
"""

from django.apps import apps
from django.core.management.base import BaseCommand, CommandError

# Import all rule modules to trigger auto-registration
import django_seo_audit.rules  # noqa: F401
from django_seo_audit import SEOAuditor
from django_seo_audit.core import SEOStatus
from django_seo_audit.mixins import SEOAuditableMixin


class Command(BaseCommand):
    """Django management command for SEO auditing with auto-discovery."""

    help = "Perform SEO audit on any model using SEOAuditableMixin"

    def add_arguments(self, parser):
        """Add command line arguments."""
        parser.add_argument(
            "--list-models",
            action="store_true",
            help="List all models that can be audited",
        )
        parser.add_argument(
            "--model",
            type=str,
            help="Model to audit in app_label.ModelName format (e.g., categories.Category)",
        )
        parser.add_argument(
            "--slug",
            type=str,
            help="Slug of the object to audit",
        )
        parser.add_argument(
            "--pk",
            type=int,
            help="Primary key of the object to audit",
        )
        parser.add_argument(
            "--category",
            type=str,
            action="append",
            help="Limit audit to specific rule categories (can be used multiple times)",
        )
        parser.add_argument(
            "--verbose",
            action="store_true",
            help="Show detailed output including suggestions",
        )

    def handle(self, *args, **options):
        """Execute the command."""
        if options["list_models"]:
            self._list_auditable_models()
            return

        # Require model argument for auditing
        if not options["model"]:
            raise CommandError("You must specify --model or use --list-models to see available models")

        # Parse model path
        try:
            app_label, model_name = options["model"].split(".")
            model_class = apps.get_model(app_label, model_name)
        except (ValueError, LookupError) as e:
            raise CommandError(f"Invalid model '{options['model']}': {e}") from None

        # Verify model uses SEOAuditableMixin
        if not self._is_auditable_model(model_class):
            raise CommandError(
                f"Model {model_class.__name__} does not use SEOAuditableMixin. "
                "Use --list-models to see available models."
            )

        # Get the object to audit
        obj = self._get_object(model_class, options)

        # Perform audit
        self._perform_audit(obj, options)

    def _list_auditable_models(self):
        """List all models that use SEOAuditableMixin."""
        self.stdout.write("Models with SEO audit capability:")
        self.stdout.write("=" * 50)
        self.stdout.write("")

        auditable_models = self._discover_auditable_models()

        if not auditable_models:
            self.stdout.write(self.style.WARNING("No auditable models found."))
            self.stdout.write("\nTo make a model auditable, add SEOAuditableMixin:")
            self.stdout.write("  from django_seo_audit import SEOAuditableMixin")
            self.stdout.write("")
            self.stdout.write("  class YourModel(SEOAuditableMixin, models.Model):")
            self.stdout.write("      # your fields here")
            return

        for app_label, model_name, model_class in auditable_models:
            model_path = f"{app_label}.{model_name}"
            try:
                count = model_class.objects.count()
                self.stdout.write(f"  • {model_path:<40} ({count} objects)")
            except Exception:
                # Database not available or model has issues - still show the model
                self.stdout.write(f"  • {model_path:<40} (database unavailable)")

        self.stdout.write("")
        self.stdout.write(f"Total: {len(auditable_models)} auditable models")
        self.stdout.write("")
        self.stdout.write("Usage example:")
        if auditable_models:
            example_app, example_model, _ = auditable_models[0]
            self.stdout.write(f"  python manage.py seo_audit --model {example_app}.{example_model} --slug <slug>")

    def _discover_auditable_models(self):
        """Discover all Django models using SEOAuditableMixin."""
        auditable_models = []

        for model in apps.get_models():
            if self._is_auditable_model(model):
                app_label = model._meta.app_label
                model_name = model.__name__
                auditable_models.append((app_label, model_name, model))

        return sorted(auditable_models, key=lambda x: (x[0], x[1]))

    def _is_auditable_model(self, model_class):
        """Check if a model uses SEOAuditableMixin."""
        # Check if SEOAuditableMixin is in the MRO
        return SEOAuditableMixin in model_class.__mro__

    def _get_object(self, model_class, options):
        """Get the object to audit based on lookup parameters."""
        slug = options.get("slug")
        pk = options.get("pk")

        if not slug and not pk:
            raise CommandError("You must specify either --slug or --pk to identify the object")

        try:
            if slug:
                obj = model_class.objects.get(slug=slug)
            else:
                obj = model_class.objects.get(pk=pk)
        except model_class.DoesNotExist:
            lookup = f"slug='{slug}'" if slug else f"pk={pk}"
            raise CommandError(f"{model_class.__name__} with {lookup} does not exist") from None
        except Exception as e:
            raise CommandError(f"Error fetching object: {e}") from None

        return obj

    def _perform_audit(self, obj, options):
        """Perform the SEO audit and display results."""
        categories = options.get("category")
        verbose = options["verbose"]

        # Get object display name
        display_name = str(obj)
        if hasattr(obj, "name"):
            display_name = obj.name
        elif hasattr(obj, "title"):
            display_name = obj.title

        # Create auditor with optional category filtering
        auditor = SEOAuditor(categories=categories)

        # Display header
        self.stdout.write(f'🔍 SEO Audit for: "{display_name}"')
        self.stdout.write(f"   Model: {obj.__class__.__name__}")
        self.stdout.write("=" * (len(display_name) + 20))
        self.stdout.write("")

        # Perform the audit
        audit_result = auditor.audit_object(obj)

        # Display results by category
        self._display_results_by_category(audit_result, verbose)

        # Display summary
        self.stdout.write("")
        self.stdout.write("Summary")
        self.stdout.write("-------")
        self.stdout.write(audit_result.get_summary_text())

        # Show overall status
        if audit_result.is_passing():
            self.stdout.write(self.style.SUCCESS("✅ SEO audit passed - no critical issues found"))
        else:
            self.stdout.write(
                self.style.WARNING(f"⚠️  SEO audit found {audit_result.critical_count} critical issue(s)")
            )

    def _display_results_by_category(self, audit_result, verbose):
        """Display audit results organized by category."""
        from django_seo_audit.registry import SEORuleRegistry

        categories = SEORuleRegistry.get_categories()

        for category in categories:
            category_rules = SEORuleRegistry.get_rules_by_category(category)
            category_results = {
                rule.name: audit_result.results[rule.name] for rule in category_rules if rule.name in audit_result.results
            }

            if not category_results:
                continue

            # Display category header
            category_title = category.replace("_", " ").title()
            self.stdout.write(f"\n{category_title}")
            self.stdout.write("-" * len(category_title))

            # Display results for this category
            for rule_name, result in category_results.items():
                self._display_single_result(rule_name, result, verbose)

    def _display_single_result(self, rule_name, result, verbose):
        """Display a single audit result with color coding."""
        # Color the output based on status
        status_color = {
            SEOStatus.GOOD: self.style.SUCCESS,
            SEOStatus.WARNING: self.style.WARNING,
            SEOStatus.CRITICAL: self.style.ERROR,
        }

        color_func = status_color.get(result.status, str)

        # Main result line
        main_message = f"{result.status.emoji} {rule_name}: {result.message}"
        self.stdout.write(color_func(main_message))

        # Additional details if available
        if result.details and verbose:
            self.stdout.write(f"   📝 {result.details}")

        # Show suggestions for warnings and critical issues
        if verbose and result.suggestions and result.status != SEOStatus.GOOD:
            self.stdout.write("   💡 Suggestions:")
            for suggestion in result.suggestions:
                self.stdout.write(f"      • {suggestion}")
