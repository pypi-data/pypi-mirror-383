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
├── pyproject.toml               # Package configuration
├── README.md                    # User documentation
├── LICENSE                      # MIT License
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
# Run linting
ruff check src/
ruff format src/

# Type checking
mypy src/

# Test in directory-builder
cd ../directory-builder
uv run python src/manage.py seo_audit --list-models
uv run python src/manage.py seo_audit --model categories.Category --slug test
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

## Testing Strategy

Since this is extracted from directory-builder, test it there:

1. Run `uv sync` in workspace root (links local package)
2. Update directory-builder imports to use `django_seo_audit`
3. Run directory-builder test suite
4. Run management command with `--list-models`
5. Audit various model types (Category, Page, Entity)

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

## Publishing Checklist

Before publishing to PyPI:

- [ ] Update version in `__init__.py` and `pyproject.toml`
- [ ] Ensure all tests pass in directory-builder
- [ ] Run `ruff check` and `ruff format`
- [ ] Run `mypy src/`
- [ ] Update README.md with any new features
- [ ] Create GitHub release
- [ ] Build and upload to PyPI: `uv build && uv publish`

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
