"""
BLACK VEIL V5 - Model Version Management
Semantic version management for ML models
"""
from typing import Dict, Any, Optional, List
from datetime import datetime
import re


class ModelVersion:
    """
    Semantic version management for ML models.

    Implements semantic versioning:
    MAJOR.MINOR.PATCH
    - MAJOR: Breaking changes (architecture changes)
    - MINOR: New features (new capabilities)
    - PATCH: Bug fixes, performance improvements
    """

    VERSION_PATTERN = re.compile(r"^(\d+)\.(\d+)\.(\d+)(-([a-zA-Z0-9.]+))?(\+([a-zA-Z0-9.]+))?$")

    def __init__(self, version: str = "1.0.0"):
        """
        Initialize version.

        Args:
            version: Version string in MAJOR.MINOR.PATCH format

        Raises:
            ValueError: If version format is invalid
        """
        self._version = version
        self._major, self._minor, self._patch, self._pre_release, self._build = (
            self._parse(version)
        )

    @staticmethod
    def _parse(version: str) -> tuple:
        """Parse version string into components."""
        match = ModelVersion.VERSION_PATTERN.match(version)
        if not match:
            raise ValueError(
                f"Invalid version format: {version}. "
                f"Expected MAJOR.MINOR.PATCH format"
            )
        return (
            int(match.group(1)),
            int(match.group(2)),
            int(match.group(3)),
            match.group(5),
            match.group(7),
        )

    @property
    def major(self) -> int:
        """Major version number."""
        return self._major

    @property
    def minor(self) -> int:
        """Minor version number."""
        return self._minor

    @property
    def patch(self) -> int:
        """Patch version number."""
        return self._patch

    @property
    def pre_release(self) -> Optional[str]:
        """Pre-release label."""
        return self._pre_release

    @property
    def build(self) -> Optional[str]:
        """Build metadata."""
        return self._build

    def __str__(self) -> str:
        version = f"{self._major}.{self._minor}.{self._patch}"
        if self._pre_release:
            version += f"-{self._pre_release}"
        if self._build:
            version += f"+{self._build}"
        return version

    def __repr__(self) -> str:
        return f"ModelVersion('{str(self)}')"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ModelVersion):
            return NotImplemented
        return (self._major, self._minor, self._patch) == (
            other._major, other._minor, other._patch
        )

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, ModelVersion):
            return NotImplemented
        return (self._major, self._minor, self._patch) < (
            other._major, other._minor, other._patch
        )

    def __le__(self, other: object) -> bool:
        if not isinstance(other, ModelVersion):
            return NotImplemented
        return (self._major, self._minor, self._patch) <= (
            other._major, other._minor, other._patch
        )

    def __gt__(self, other: object) -> bool:
        if not isinstance(other, ModelVersion):
            return NotImplemented
        return (self._major, self._minor, self._patch) > (
            other._major, other._minor, other._patch
        )

    def __ge__(self, other: object) -> bool:
        if not isinstance(other, ModelVersion):
            return NotImplemented
        return (self._major, self._minor, self._patch) >= (
            other._major, other._minor, other._patch
        )

    def __hash__(self) -> int:
        return hash(str(self))

    def bump_major(self) -> "ModelVersion":
        """Bump major version (breaking changes)."""
        return ModelVersion(f"{self._major + 1}.0.0")

    def bump_minor(self) -> "ModelVersion":
        """Bump minor version (new features)."""
        return ModelVersion(f"{self._major}.{self._minor + 1}.0")

    def bump_patch(self) -> "ModelVersion":
        """Bump patch version (bug fixes)."""
        return ModelVersion(f"{self._major}.{self._minor}.{self._patch + 1}")

    @staticmethod
    def is_compatible(version1: str, version2: str) -> bool:
        """
        Check if two versions are compatible (same major version).

        Args:
            version1: First version string
            version2: Second version string

        Returns:
            bool: True if compatible
        """
        v1 = ModelVersion(version1)
        v2 = ModelVersion(version2)
        return v1.major == v2.major

    @staticmethod
    def get_latest(versions: List[str]) -> str:
        """
        Get the latest version from a list.

        Args:
            versions: List of version strings

        Returns:
            str: Latest version
        """
        if not versions:
            raise ValueError("Empty version list")

        parsed = [ModelVersion(v) for v in versions]
        return str(max(parsed))

    @staticmethod
    def sort_versions(versions: List[str]) -> List[str]:
        """
        Sort versions in ascending order.

        Args:
            versions: List of version strings

        Returns:
            List[str]: Sorted versions
        """
        parsed = [ModelVersion(v) for v in versions]
        parsed.sort()
        return [str(v) for v in parsed]

    @staticmethod
    def create_training_version(
        base_version: str,
        accuracy: float,
        data_version: str
    ) -> str:
        """
        Create a version string for a training run.

        Args:
            base_version: Base model version
            accuracy: Model accuracy
            data_version: Training data version

        Returns:
            str: Training version string
        """
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        acc_str = f"{accuracy:.4f}".replace(".", "")
        return f"{base_version}+train.{timestamp}.acc{acc_str}.data{data_version}"
