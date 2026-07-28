"""
BLACK VEIL V5 - Data Utilities
Data preprocessing and transformation utilities
"""
from typing import Dict, Any, Optional, List, Tuple, Union
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler, MinMaxScaler, LabelEncoder
from sklearn.model_selection import train_test_split
import torch
from torch.utils.data import Dataset, DataLoader


class SecurityDataset(Dataset):
    """PyTorch Dataset for security data."""

    def __init__(
        self,
        features: np.ndarray,
        labels: Optional[np.ndarray] = None,
        transform: Optional[callable] = None,
    ):
        """
        Initialize dataset.

        Args:
            features: Feature array
            labels: Optional label array
            transform: Optional transform function
        """
        self.features = torch.FloatTensor(features)
        self.labels = torch.LongTensor(labels) if labels is not None else None
        self.transform = transform

    def __len__(self) -> int:
        return len(self.features)

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, Optional[torch.Tensor]]:
        x = self.features[idx]
        if self.transform:
            x = self.transform(x)

        if self.labels is not None:
            return x, self.labels[idx]
        return x, None


class DataUtils:
    """Utility class for data preprocessing and transformation."""

    @staticmethod
    def normalize(
        data: np.ndarray,
        method: str = "standard",
        scaler: Optional[Union[StandardScaler, MinMaxScaler]] = None
    ) -> Tuple[np.ndarray, Optional[Union[StandardScaler, MinMaxScaler]]]:
        """
        Normalize data using specified method.

        Args:
            data: Input data array
            method: Normalization method ('standard' or 'minmax')
            scaler: Optional pre-fitted scaler

        Returns:
            Tuple[np.ndarray, Optional[Union[StandardScaler, MinMaxScaler]]]:
                Normalized data and scaler
        """
        if scaler is None:
            if method == "standard":
                scaler = StandardScaler()
            elif method == "minmax":
                scaler = MinMaxScaler()
            else:
                raise ValueError(f"Unknown normalization method: {method}")
            normalized = scaler.fit_transform(data)
        else:
            normalized = scaler.transform(data)

        return normalized, scaler

    @staticmethod
    def encode_labels(
        labels: np.ndarray,
        encoder: Optional[LabelEncoder] = None
    ) -> Tuple[np.ndarray, Optional[LabelEncoder]]:
        """
        Encode categorical labels.

        Args:
            labels: Input labels
            encoder: Optional pre-fitted encoder

        Returns:
            Tuple[np.ndarray, Optional[LabelEncoder]]:
                Encoded labels and encoder
        """
        if encoder is None:
            encoder = LabelEncoder()
            encoded = encoder.fit_transform(labels)
        else:
            encoded = encoder.transform(labels)

        return encoded, encoder

    @staticmethod
    def split_data(
        features: np.ndarray,
        labels: np.ndarray,
        test_size: float = 0.2,
        val_size: float = 0.1,
        random_state: int = 42,
        stratify: bool = True,
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        Split data into train, validation, and test sets.

        Args:
            features: Feature array
            labels: Label array
            test_size: Test set ratio
            val_size: Validation set ratio
            random_state: Random seed
            stratify: Whether to stratify splits

        Returns:
            Tuple containing X_train, X_val, X_test, y_train, y_val, y_test
        """
        stratify_data = labels if stratify else None

        # First split: train+val vs test
        X_temp, X_test, y_temp, y_test = train_test_split(
            features, labels,
            test_size=test_size,
            random_state=random_state,
            stratify=stratify_data,
        )

        # Second split: train vs val
        val_ratio = val_size / (1 - test_size)
        X_train, X_val, y_train, y_val = train_test_split(
            X_temp, y_temp,
            test_size=val_ratio,
            random_state=random_state,
            stratify=y_temp if stratify else None,
        )

        return X_train, X_val, X_test, y_train, y_val, y_test

    @staticmethod
    def create_dataloaders(
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_val: Optional[np.ndarray] = None,
        y_val: Optional[np.ndarray] = None,
        X_test: Optional[np.ndarray] = None,
        y_test: Optional[np.ndarray] = None,
        batch_size: int = 32,
        num_workers: int = 4,
        shuffle: bool = True,
    ) -> Dict[str, DataLoader]:
        """
        Create PyTorch DataLoaders.

        Args:
            X_train: Training features
            y_train: Training labels
            X_val: Validation features
            y_val: Validation labels
            X_test: Test features
            y_test: Test labels
            batch_size: Batch size
            num_workers: Number of worker processes
            shuffle: Whether to shuffle training data

        Returns:
            Dict[str, DataLoader]: DataLoaders for each split
        """
        loaders = {}

        train_dataset = SecurityDataset(X_train, y_train)
        loaders["train"] = DataLoader(
            train_dataset,
            batch_size=batch_size,
            shuffle=shuffle,
            num_workers=num_workers,
            pin_memory=True,
        )

        if X_val is not None and y_val is not None:
            val_dataset = SecurityDataset(X_val, y_val)
            loaders["val"] = DataLoader(
                val_dataset,
                batch_size=batch_size,
                shuffle=False,
                num_workers=num_workers,
                pin_memory=True,
            )

        if X_test is not None and y_test is not None:
            test_dataset = SecurityDataset(X_test, y_test)
            loaders["test"] = DataLoader(
                test_dataset,
                batch_size=batch_size,
                shuffle=False,
                num_workers=num_workers,
                pin_memory=True,
            )

        return loaders

    @staticmethod
    def compute_class_weights(
        labels: np.ndarray,
        method: str = "balanced"
    ) -> torch.Tensor:
        """
        Compute class weights for imbalanced datasets.

        Args:
            labels: Label array
            method: Weight computation method

        Returns:
            torch.Tensor: Class weights
        """
        from sklearn.utils.class_weight import compute_class_weight

        classes = np.unique(labels)
        weights = compute_class_weight(method, classes=classes, y=labels)
        return torch.FloatTensor(weights)

    @staticmethod
    def prepare_features(
        data: Dict[str, Any],
        feature_columns: List[str],
        fill_value: float = 0.0
    ) -> np.ndarray:
        """
        Prepare feature vector from data dictionary.

        Args:
            data: Input data dictionary
            feature_columns: Ordered list of feature names
            fill_value: Default value for missing features

        Returns:
            np.ndarray: Feature array
        """
        features = []
        for col in feature_columns:
            value = data.get(col, fill_value)
            if isinstance(value, (int, float)):
                features.append(float(value))
            else:
                features.append(fill_value)

        return np.array([features], dtype=np.float32)

    @staticmethod
    def handle_missing_values(
        df: pd.DataFrame,
        strategy: str = "mean"
    ) -> pd.DataFrame:
        """
        Handle missing values in DataFrame.

        Args:
            df: Input DataFrame
            strategy: Imputation strategy

        Returns:
            pd.DataFrame: DataFrame with handled missing values
        """
        df = df.copy()

        for col in df.columns:
            if df[col].isnull().sum() > 0:
                if df[col].dtype in {np.float64, np.float32, np.int64, np.int32}:
                    if strategy == "mean":
                        df[col].fillna(df[col].mean(), inplace=True)
                    elif strategy == "median":
                        df[col].fillna(df[col].median(), inplace=True)
                    elif strategy == "zero":
                        df[col].fillna(0, inplace=True)
                else:
                    df[col].fillna(df[col].mode()[0] if not df[col].mode().empty else "unknown", inplace=True)

        return df

    @staticmethod
    def remove_outliers(
        df: pd.DataFrame,
        columns: List[str],
        method: str = "iqr",
        threshold: float = 3.0
    ) -> pd.DataFrame:
        """
        Remove outliers from DataFrame columns.

        Args:
            df: Input DataFrame
            columns: Columns to check for outliers
            method: Outlier detection method
            threshold: Detection threshold

        Returns:
            pd.DataFrame: DataFrame with outliers removed
        """
        df = df.copy()
        mask = pd.Series([True] * len(df))

        for col in columns:
            if method == "iqr":
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                col_mask = ~((df[col] < (Q1 - 1.5 * IQR)) | (df[col] > (Q3 + 1.5 * IQR)))
            elif method == "zscore":
                z_scores = np.abs((df[col] - df[col].mean()) / df[col].std())
                col_mask = z_scores < threshold
            else:
                raise ValueError(f"Unknown outlier method: {method}")

            mask = mask & col_mask

        return df[mask]
