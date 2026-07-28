"""
BLACK VEIL V5 - Validation Utilities
Input validation, schema validation, and data quality checks
"""
from typing import Dict, Any, Optional, List, Tuple, Union
import numpy as np
import pandas as pd
from datetime import datetime


class ValidationError(Exception):
    """Custom exception for validation failures."""
    pass


class ValidationUtils:
    """Utility class for input and data validation."""

    @staticmethod
    def validate_required_fields(
        data: Dict[str, Any],
        required_fields: List[str],
        strict: bool = False,
    ) -> Tuple[bool, List[str]]:
        """
        Validate that all required fields are present.

        Args:
            data: Input data dictionary
            required_fields: List of required field names
            strict: If True, also ensure no extra fields

        Returns:
            Tuple[bool, List[str]]: Validation result and error messages
        """
        errors = []

        for field in required_fields:
            if field not in data:
                errors.append(f"Missing required field: '{field}'")
            elif data[field] is None:
                errors.append(f"Field '{field}' is None")

        if strict:
            extra_fields = set(data.keys()) - set(required_fields)
            if extra_fields:
                errors.append(f"Unexpected fields: {extra_fields}")

        return len(errors) == 0, errors

    @staticmethod
    def validate_numeric_range(
        value: float,
        min_val: float,
        max_val: float,
        field_name: str = "value",
        inclusive: bool = True,
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate that a numeric value is within range.

        Args:
            value: Numeric value
            min_val: Minimum allowed value
            max_val: Maximum allowed value
            field_name: Field name for error message
            inclusive: If True, include boundaries

        Returns:
            Tuple[bool, Optional[str]]: Validation result and error message
        """
        if inclusive:
            if value < min_val or value > max_val:
                return False, (
                    f"'{field_name}' must be in [{min_val}, {max_val}], "
                    f"got {value}"
                )
        else:
            if value <= min_val or value >= max_val:
                return False, (
                    f"'{field_name}' must be in ({min_val}, {max_val}), "
                    f"got {value}"
                )

        return True, None

    @staticmethod
    def validate_array_shape(
        array: np.ndarray,
        expected_shape: Tuple[Optional[int], ...],
        field_name: str = "array",
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate array shape.

        Args:
            array: Input array
            expected_shape: Expected shape (None means any size)
            field_name: Field name for error message

        Returns:
            Tuple[bool, Optional[str]]: Validation result and error message
        """
        if len(array.shape) != len(expected_shape):
            return False, (
                f"'{field_name}' expected {len(expected_shape)} dimensions, "
                f"got {len(array.shape)}"
            )

        for i, (actual, expected) in enumerate(zip(array.shape, expected_shape)):
            if expected is not None and actual != expected:
                return False, (
                    f"'{field_name}' dimension {i} expected {expected}, "
                    f"got {actual}"
                )

        return True, None

    @staticmethod
    def validate_probability(
        value: float,
        field_name: str = "probability",
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate a probability value.

        Args:
            value: Probability value
            field_name: Field name for error message

        Returns:
            Tuple[bool, Optional[str]]: Validation result and error message
        """
        return ValidationUtils.validate_numeric_range(
            value, 0.0, 1.0, field_name
        )

    @staticmethod
    def validate_trust_score(
        value: float,
        field_name: str = "trust_score",
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate a trust score (0-100).

        Args:
            value: Trust score
            field_name: Field name for error message

        Returns:
            Tuple[bool, Optional[str]]: Validation result and error message
        """
        return ValidationUtils.validate_numeric_range(
            value, 0.0, 100.0, field_name
        )

    @staticmethod
    def validate_data_quality(
        df: pd.DataFrame,
        min_rows: int = 1,
        max_missing_ratio: float = 0.5,
    ) -> Dict[str, Any]:
        """
        Assess data quality of a DataFrame.

        Args:
            df: Input DataFrame
            min_rows: Minimum required rows
            max_missing_ratio: Maximum allowed missing value ratio

        Returns:
            Dict[str, Any]: Data quality report
        """
        quality = {
            "n_rows": len(df),
            "n_columns": len(df.columns),
            "n_missing": int(df.isnull().sum().sum()),
            "missing_ratio": float(df.isnull().sum().sum() / (df.size if df.size > 0 else 1)),
            "n_duplicates": int(df.duplicated().sum()),
            "duplicate_ratio": float(df.duplicated().sum() / len(df) if len(df) > 0 else 0),
            "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
            "columns_with_missing": [
                col for col in df.columns if df[col].isnull().sum() > 0
            ],
            "passes_quality": True,
            "warnings": [],
        }

        if len(df) < min_rows:
            quality["passes_quality"] = False
            quality["warnings"].append(
                f"DataFrame has {len(df)} rows, minimum is {min_rows}"
            )

        if quality["missing_ratio"] > max_missing_ratio:
            quality["passes_quality"] = False
            quality["warnings"].append(
                f"Missing ratio {quality['missing_ratio']:.2%} exceeds "
                f"maximum {max_missing_ratio:.2%}"
            )

        return quality

    @staticmethod
    def validate_feature_vector(
        features: Dict[str, Any],
        expected_features: List[str],
        feature_types: Optional[Dict[str, type]] = None,
    ) -> Tuple[bool, List[str]]:
        """
        Validate a feature vector.

        Args:
            features: Feature dictionary
            expected_features: List of expected feature names
            feature_types: Optional dictionary of expected feature types

        Returns:
            Tuple[bool, List[str]]: Validation result and error messages
        """
        errors = []

        # Check required features
        for feat in expected_features:
            if feat not in features:
                errors.append(f"Missing feature: '{feat}'")
                continue

            value = features[feat]
            if value is None:
                errors.append(f"Feature '{feat}' is None")

            # Check type
            if feature_types and feat in feature_types:
                expected_type = feature_types[feat]
                if not isinstance(value, expected_type):
                    errors.append(
                        f"Feature '{feat}' expected type {expected_type.__name__}, "
                        f"got {type(value).__name__}"
                    )

        # Check for unexpected features
        unexpected = set(features.keys()) - set(expected_features)
        if unexpected:
            errors.append(f"Unexpected features: {unexpected}")

        return len(errors) == 0, errors

    @staticmethod
    def validate_timestamp_format(
        timestamp: str,
        format: str = "%Y-%m-%dT%H:%M:%S",
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate timestamp string format.

        Args:
            timestamp: Timestamp string
            format: Expected format

        Returns:
            Tuple[bool, Optional[str]]: Validation result and error message
        """
        try:
            datetime.strptime(timestamp, format)
            return True, None
        except ValueError:
            return False, f"Timestamp '{timestamp}' does not match format '{format}'"

    @staticmethod
    def validate_string_length(
        value: str,
        min_length: int = 0,
        max_length: int = 256,
        field_name: str = "string",
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate string length.

        Args:
            value: String value
            min_length: Minimum length
            max_length: Maximum length
            field_name: Field name for error message

        Returns:
            Tuple[bool, Optional[str]]: Validation result and error message
        """
        if len(value) < min_length:
            return False, (
                f"'{field_name}' length {len(value)} is less than "
                f"minimum {min_length}"
            )
        if len(value) > max_length:
            return False, (
                f"'{field_name}' length {len(value)} exceeds "
                f"maximum {max_length}"
            )
        return True, None

    @staticmethod
    def sanitize_input(value: str) -> str:
        """
        Sanitize string input for security.

        Args:
            value: Input string

        Returns:
            str: Sanitized string
        """
        import re
        # Remove potentially dangerous characters
        sanitized = re.sub(r"[<>\";'()&|\\]", "", value)
        # Limit length
        sanitized = sanitized[:1000]
        return sanitized
