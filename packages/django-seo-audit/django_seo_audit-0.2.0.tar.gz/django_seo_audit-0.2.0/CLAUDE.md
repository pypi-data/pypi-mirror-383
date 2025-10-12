# CLAUDE.md - Django SEO Audit Package

This file provides guidance to Claude Code when working with the `django-seo-audit` package.

## Project Overview

**Django SEO Audit** is a standalone Django package providing protocol-based SEO auditing for Django models. It uses Python 3.12+ protocols for loose coupling and features automatic rule discovery.

**Key Features**:
- Protocol-based architecture (no inheritance required)
- Auto-registration of SEO rules via `__init_subclass__`
- Auto-discovery management command finds all auditable models
- 18 built-in rules across 4 categories
- Beautiful CLI output with emoji indicators
- Extensible for custom SEO rules

## Package Structure

```
django-seo-audit/
├── src/django_seo_audit/
│   ├── __init__.py              # Public API exports
│   ├── core.py                  # SEOStatus, SEOResult, SEORule
│   ├── protocols.py             # Protocol definitions
│   ├── registry.py              # SEORuleRegistry, SEOAuditor
│   ├── mixins.py                # SEOAuditableMixin for Django models
│   ├── rules/
│   │   ├── __init__.py          # Auto-imports all rules
│   │   ├── core_seo_rules.py    # 5 core SEO rules
│   │   ├── social_media_rules.py # 5 social media rules
│   │   ├── content_rules.py     # 4 content quality rules
│   │   └── technical_seo_rules.py # 4 technical SEO rules
│   └── management/
│       └── commands/
│           └── seo_audit.py     # Auto-discovery management command
├── tests/                       # Comprehensive test suite (207 tests)
│   ├── settings.py              # Test Django configuration
│   ├── manage.py                # Django test runner
│   ├── example_app/             # Living documentation models
│   │   ├── __init__.py
│   │   ├── apps.py
│   │   ├── models.py            # BlogPost, Product, Page
│   │   └── migrations/
│   ├── test_core.py             # Core component tests (28)
│   ├── test_protocols.py        # Protocol tests (7)
│   ├── test_registry.py         # Registry tests (24)
│   ├── test_mixins.py           # Mixin tests (43)
│   ├── test_rules.py            # Rule tests (58)
│   └── test_management_commands.py  # CLI tests (19)
├── pyproject.toml               # Package configuration
├── README.md                    # User documentation
├── LICENSE                      # MIT License
├── Makefile                     # Development commands
└── CLAUDE.md                    # This file
```

## Development Setup

This package is part of the Directory Platform workspace. Use UV for dependency management:

```bash
# From workspace root
cd django-seo-audit
uv sync --extra dev

# Or from workspace root
uv sync
```

## Code Patterns

### Protocol-Based Design

Rules check against protocols, not concrete classes:

```python
from django_seo_audit.protocols import BasicSEOAuditable

class MyRule(SEORule):
    def check(self, obj: BasicSEOAuditable) -> SEOResult:
        # Type hints indicate what methods obj must implement
        title = obj.get_seo_title()
        # ...
```

### Auto-Registration

Rules auto-register via metaclass:

```python
class SEORule(ABC):
    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        if cls.name and cls.name != "":
            from .registry import SEORuleRegistry
            SEORuleRegistry.register(cls)
```

**Important**: Only concrete rules with `name` attribute are registered.

### Immutable Results

`SEOResult` uses frozen dataclass for thread-safety:

```python
@dataclass(frozen=True)
class SEOResult:
    status: SEOStatus
    message: str
    details: str = ""
    score: int = 0  # 0-10 scale
    suggestions: list[str] | None = None
```

### Intelligent Fallbacks

The mixin provides fallback chains:

```python
def get_seo_title(self) -> str:
    return getattr(self, "seo_title", "") or getattr(self, "name", "")
```

## Critical Constraints

### NEVER Do These

- ❌ Break the Protocol interface contracts
- ❌ Modify rule weights without understanding impact on scoring
- ❌ Add rules without proper category assignment
- ❌ Use mutable data structures in SEOResult
- ❌ Import Django models in protocols.py (keeps it decoupled)

### ALWAYS Do These

- ✅ Import all rule modules to trigger auto-registration
- ✅ Use frozen dataclass for SEOResult
- ✅ Provide helpful suggestions for non-GOOD results
- ✅ Score on 0-10 scale (validated in SEOResult.__post_init__)
- ✅ Check if model uses SEOAuditableMixin before auditing

## Common Commands

```bash
# Run tests
make test
# or
PYTHONPATH=. uv run python tests/manage.py test

# Run linting
ruff check src/ tests/
ruff format src/ tests/

# Type checking
mypy src/

# Run all checks (lint + typecheck + test)
make check
```

## Adding New Rules

1. Create rule in appropriate file (or new file in `rules/`)
2. Extend SEORule and implement `check()` method
3. Set name, description, category, weight
4. Return SEOResult with appropriate status and score
5. Import in `rules/__init__.py` (auto-registration happens)

Example:

```python
# rules/custom_rules.py
from ..core import SEOResult, SEORule, SEOStatus
from ..protocols import BasicSEOAuditable

class MyCustomRule(SEORule):
    name = "My Custom Rule"
    description = "Checks something important"
    category = "core_seo"
    weight = 3

    def check(self, obj: BasicSEOAuditable) -> SEOResult:
        # Your logic
        return SEOResult(
            status=SEOStatus.GOOD,
            message="All good!",
            score=10,
        )
```

## Testing

This package has a comprehensive standalone test suite with 207 tests covering all components.

### Test Structure

```
tests/
├── settings.py              # Test Django configuration
├── manage.py                # Django test runner
├── example_app/             # Living documentation with 3 models
│   ├── models.py            # BlogPost, Product, Page examples
│   └── migrations/          # Auto-generated migrations
├── test_core.py             # Core components (28 tests)
├── test_protocols.py        # Protocol compliance (7 tests)
├── test_registry.py         # Registry & auditor (24 tests)
├── test_mixins.py           # Mixin functionality (43 tests)
├── test_rules.py            # All 18 built-in rules (58 tests)
└── test_management_commands.py  # CLI commands (19 tests)
```

### Running Tests

```bash
# Run all tests (207 tests)
PYTHONPATH=. uv run python tests/manage.py test

# Run with verbose output
PYTHONPATH=. uv run python tests/manage.py test --verbosity=2

# Run specific test module
PYTHONPATH=. uv run python tests/manage.py test tests.test_rules

# Run specific test class
PYTHONPATH=. uv run python tests/manage.py test tests.test_rules.SEOTitleLengthRuleTest

# Or use the Makefile
make test
make test-verbose
```

### Example Models (Living Documentation)

The `tests/example_app/` contains 3 example implementations:

1. **BlogPost** - Full SEO implementation with all fields
2. **Product** - Minimal implementation showing fallbacks
3. **Page** - Custom protocol implementation without mixin

These serve as both test fixtures and living documentation for package users.

## Architecture Decisions

### Why Protocols?

Structural subtyping allows any object to be auditable without inheritance. Models just implement methods - no base class needed.

### Why Auto-Registration?

Reduces boilerplate and ensures rules are discovered automatically. No need to maintain a central registry list.

### Why Frozen Dataclass?

SEOResult is immutable and thread-safe. Results can be safely cached and compared.

### Why Weight System?

Different rules have different importance. Title optimization (weight=5) matters more than secondary keywords (weight=2).

## Scoring Algorithm

```python
# In SEOAuditResult._calculate_summary()
total_score = sum(result.score for result in self.results.values())
self.overall_score = round(total_score / (self.total_rules * 10) * 10, 1)
```

- Each rule scores 0-10
- Overall score is average normalized to 0-10
- Letter grades: A (9+), B (8+), C (7+), D (6+), F (<6)

## Extension Points

1. **Custom Protocols**: Define new protocol contracts
2. **Custom Rules**: Implement SEORule with custom logic
3. **Custom Categories**: Add new category strings
4. **Mixin Override**: Extend SEOAuditableMixin for project-specific needs

## Publishing to PyPI (Automated)

This package uses **GitHub Actions** to automatically publish to PyPI when a release is created. The workflow is configured with PyPI Trusted Publishers (no API tokens needed).

### Release Process (Follow These Steps)

**1. Update Version Number**

Edit `pyproject.toml` and bump the version:

```toml
[project]
version = "0.1.1"  # Change this
```

Also update version in `src/django_seo_audit/__init__.py`:

```python
__version__ = "0.1.1"  # Change this
```

**2. Pre-Release Checks**

Run these commands before releasing:

```bash
# Run all checks (lint + typecheck + test)
make check

# Or run individually:

# Run tests
make test

# Lint and format
ruff check src/ tests/
ruff format src/ tests/

# Type check
mypy src/
```

**3. Commit Version Bump**

```bash
git add pyproject.toml src/django_seo_audit/__init__.py
git commit -m "Bump version to 0.1.1"
git push origin master
```

**4. Create GitHub Release**

Use GitHub CLI to create a release (tag and version must match):

```bash
gh release create v0.1.1 \
  --title "Release v0.1.1" \
  --notes "
## What's Changed

- Feature: Added X functionality
- Fix: Resolved issue with Y
- Docs: Updated Z documentation

**Full Changelog**: https://github.com/heysamtexas/django-seo-audit/compare/v0.1.0...v0.1.1
"
```

**5. Verify Workflow Success**

The GitHub Actions workflow will automatically:

1. ✅ Verify version in `pyproject.toml` matches git tag
2. ✅ Install dependencies with UV
3. ✅ Run import tests
4. ✅ Build the package
5. ✅ Publish to PyPI using Trusted Publisher

Monitor the workflow:

```bash
# Check latest run status
gh run list --repo heysamtexas/django-seo-audit --limit 1

# Watch workflow in real-time (get ID from above)
gh run watch <run-id> --repo heysamtexas/django-seo-audit
```

**6. Verify on PyPI**

After workflow completes, verify the package:

```bash
# Check PyPI has the new version
curl -s https://pypi.org/pypi/django-seo-audit/json | \
  python -c "import sys, json; data=json.load(sys.stdin); print(f\"Latest version: {data['info']['version']}\")"
```

### Version Bumping Guide

Follow semantic versioning (MAJOR.MINOR.PATCH):

- **PATCH** (0.1.1 → 0.1.2): Bug fixes, documentation updates
- **MINOR** (0.1.2 → 0.2.0): New features, backward compatible
- **MAJOR** (0.2.0 → 1.0.0): Breaking changes

### Troubleshooting Failed Releases

**Workflow Failed: "Version mismatch"**

The version in `pyproject.toml` must match the git tag:

```bash
# If tag is v0.1.1, version must be "0.1.1" (no 'v' prefix in pyproject.toml)
```

**Workflow Failed: "No virtual environment"**

This is already fixed in the workflow with `--system` flag. If it happens:

```bash
# Check the workflow uses:
uv pip install --system -e ".[dev]"
```

**Workflow Failed: "Import test failed"**

Ensure `__version__` in `__init__.py` is updated:

```bash
# Check version is exported
grep "__version__" src/django_seo_audit/__init__.py
```

**Need to Delete a Release**

If you need to retry a release:

```bash
# Delete release and tag
gh release delete v0.1.1 --repo heysamtexas/django-seo-audit --yes
git push origin :refs/tags/v0.1.1

# Fix issues, then recreate release
gh release create v0.1.1 --title "Release v0.1.1" --notes "Release notes"
```

### Release Template

Use this template for consistent release notes:

```markdown
## 🎉 Release v0.1.1

Brief description of the release.

### ✨ New Features
- Feature description

### 🐛 Bug Fixes
- Fix description

### 📚 Documentation
- Documentation updates

### 🔧 Technical Changes
- Internal improvements

**Full Changelog**: https://github.com/heysamtexas/django-seo-audit/compare/v0.1.0...v0.1.1
```

### PyPI Trusted Publisher (Already Configured)

This package uses PyPI Trusted Publishers for secure, token-free publishing:

- **PyPI Project**: django-seo-audit
- **GitHub Owner**: heysamtexas
- **Repository**: django-seo-audit
- **Workflow**: publish.yml

No API tokens needed! The GitHub Actions workflow authenticates using OIDC.

## Troubleshooting

**Rules not being discovered:**
- Ensure rule module is imported in `rules/__init__.py`
- Check that `name` attribute is non-empty
- Verify `__init_subclass__` is being called

**Management command not finding models:**
- Model must inherit from SEOAuditableMixin
- Model must be in INSTALLED_APPS
- Django must have loaded the model

**Type errors with protocols:**
- Protocols use structural subtyping
- Object must implement all protocol methods
- Method signatures must match exactly

## Related Files

- **workspace CLAUDE.md**: `/Users/samtexas/src/directory-platform/CLAUDE.md`
- **directory-builder CLAUDE.md**: `/Users/samtexas/src/directory-builder/CLAUDE.md`
- **README.md**: User-facing documentation
- **pyproject.toml**: Package configuration

## Quick Reference

**Import conventions:**
```python
from django_seo_audit import (
    SEOAuditor,              # Main auditor class
    SEORule,                 # Base class for rules
    SEOResult,               # Result container
    SEOStatus,               # Status enum
    SEOAuditableMixin,       # Django model mixin
    BasicSEOAuditable,       # Protocol definitions
)
```

**Scoring guide:**
- 10 = Perfect (meets best practices exactly)
- 7-9 = Good (minor improvements possible)
- 4-6 = Warning (needs attention)
- 0-3 = Critical (immediate action required)

**Rule categories:**
- `core_seo` - Essential SEO (title, description, keywords)
- `social_media` - OpenGraph, Twitter Cards
- `content` - Content quality and depth
- `technical_seo` - Structured data, robots, canonicals

## Code Style

- Line length: 120 characters
- Python 3.12+ syntax (use `|` for unions, not `Union`)
- Type hints required on all public methods
- Docstrings in Google style
- Use double quotes for strings
- Use f-strings for interpolation

## Dependencies

**Runtime:**
- Django 4.2+

**Development:**
- ruff (linting and formatting)
- mypy (type checking)
- django-stubs (Django type stubs)

No other dependencies! Keep it lightweight.
