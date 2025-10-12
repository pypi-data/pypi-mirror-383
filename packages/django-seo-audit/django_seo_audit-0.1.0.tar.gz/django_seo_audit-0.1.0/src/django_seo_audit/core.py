"""Core SEO audit classes and data structures.

This module provides the foundational classes for the SEO audit system:
- SEOStatus: Enum for audit result status levels
- SEOResult: Data class for individual rule check results
- SEORule: Abstract base class for all SEO audit rules
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any

# Constants for SEO scoring
SEO_SCORE_MIN = 0
SEO_SCORE_MAX = 10


class SEOStatus(Enum):
    """Status levels for SEO audit results with semantic meaning.

    These map to visual indicators:
    - GOOD: 🟢 Green (meets best practices)
    - WARNING: 🟡 Yellow (passing but room for improvement)
    - CRITICAL: 🔴 Red (needs immediate attention)
    """

    GOOD = "good"
    WARNING = "warning"
    CRITICAL = "critical"

    def __str__(self) -> str:
        """Return string representation for display."""
        return self.value

    @property
    def emoji(self) -> str:
        """Return emoji indicator for console output."""
        emoji_map = {
            SEOStatus.GOOD: "🟢",
            SEOStatus.WARNING: "🟡",
            SEOStatus.CRITICAL: "🔴",
        }
        return emoji_map[self]

    @property
    def color_code(self) -> str:
        """Return ANSI color code for terminal output."""
        color_map = {
            SEOStatus.GOOD: "\033[92m",  # Green
            SEOStatus.WARNING: "\033[93m",  # Yellow
            SEOStatus.CRITICAL: "\033[91m",  # Red
        }
        return color_map[self]


@dataclass(frozen=True)
class SEOResult:
    """Immutable result of an SEO rule check.

    Contains all information needed to display audit results and calculate
    overall SEO health scores.
    """

    status: SEOStatus
    message: str
    details: str = ""
    score: int = 0  # 0-10 scale for weighted scoring
    suggestions: list[str] | None = None

    def __post_init__(self) -> None:
        """Validate result data after initialization."""
        if not SEO_SCORE_MIN <= self.score <= SEO_SCORE_MAX:
            raise ValueError(f"Score must be {SEO_SCORE_MIN}-{SEO_SCORE_MAX}, got {self.score}")

        if not self.message.strip():
            raise ValueError("Message cannot be empty")

    @property
    def is_passing(self) -> bool:
        """Return True if result is acceptable (good or warning)."""
        return self.status in (SEOStatus.GOOD, SEOStatus.WARNING)

    @property
    def display_message(self) -> str:
        """Return formatted message for console display."""
        base = f"{self.status.emoji} {self.message}"
        if self.details:
            base += f" ({self.details})"
        return base

    def get_suggestions_text(self) -> str:
        """Return formatted suggestions text."""
        if not self.suggestions:
            return ""

        suggestions_list = "\n".join(f"  • {suggestion}" for suggestion in self.suggestions)
        return f"\n  Suggestions:\n{suggestions_list}"


class SEORule(ABC):
    """Abstract base class for all SEO audit rules.

    This class provides the contract that all SEO rules must implement.
    Rules are auto-registered when defined and can specify their category,
    importance weight, and target object protocols.
    """

    # Class attributes that must be overridden
    name: str = ""
    description: str = ""
    category: str = "general"
    weight: int = 1  # 1-5 importance scale (5 = most critical)

    def __init_subclass__(cls, **kwargs) -> None:
        """Auto-register rule classes when they're defined.

        This allows rules to be automatically discovered without manual
        registration, making the system truly extensible.
        """
        super().__init_subclass__(**kwargs)
        if cls.name and cls.name != "":  # Only register concrete rules
            from .registry import SEORuleRegistry

            SEORuleRegistry.register(cls)

    @abstractmethod
    def check(self, obj: Any) -> SEOResult:
        """Perform the SEO check on the given object.

        Args:
            obj: Object to audit (should implement relevant Protocol)

        Returns:
            SEOResult with status, message, score, and recommendations

        Raises:
            NotImplementedError: If not implemented by subclass

        """
        raise NotImplementedError("Subclasses must implement check() method")

    def __str__(self) -> str:
        """Return string representation for debugging."""
        return f"{self.__class__.__name__}(name='{self.name}', category='{self.category}')"

    def __repr__(self) -> str:
        """Return detailed representation for debugging."""
        return f"{self.__class__.__name__}(name='{self.name}', category='{self.category}', weight={self.weight})"

    @classmethod
    def get_protocol_requirements(cls) -> list[str]:
        """Return list of protocol method names this rule requires.

        This can be used for dynamic validation and documentation.
        Subclasses can override to specify their protocol dependencies.
        """
        return []

    def is_applicable_to(self, obj: Any) -> bool:
        """Check if this rule can be applied to the given object.

        By default, assumes all rules are applicable. Subclasses can
        override to add specific object type or capability checks.
        """
        return True
