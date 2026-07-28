"""
BLACK VEIL V5 - Feature Fusion
Multi-source feature fusion for holistic security context
"""
from typing import Dict, Any, Optional, List, Tuple
import numpy as np
import logging
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class FusedFeatures:
    """Container for fused feature results."""
    fused_vector: np.ndarray
    feature_importance: Dict[str, float]
    source_contributions: Dict[str, float]
    dimension_reduction_applied: bool
    n_original_features: int
    n_fused_features: int
    fusion_method: str


class FeatureFusion:
    """
    Feature fusion module for combining features from multiple sources.

    Supports:
    - Concatenation fusion
    - Weighted sum fusion
    - Attention-based fusion
    - PCA/SVD dimension reduction
    - Feature importance calculation
    """

    def __init__(self, method: str = "concatenation"):
        """
        Initialize feature fusion.

        Args:
            method: Fusion method to use
        """
        self.method = method
        self._feature_means: Dict[str, np.ndarray] = {}
        self._feature_stds: Dict[str, np.ndarray] = {}
        self._pca_components: Optional[np.ndarray] = None
        self._attention_weights: Dict[str, float] = {}

    def fuse_concatenation(
        self,
        features: Dict[str, np.ndarray]
    ) -> FusedFeatures:
        """Simple concatenation of all feature vectors."""
        vectors = []
        contributions = {}

        for source, vec in features.items():
            flat = vec.flatten()
            vectors.append(flat)
            contributions[source] = float(len(flat))

        fused = np.concatenate(vectors)
        total = sum(contributions.values())

        contributions = {k: v / total for k, v in contributions.items()}

        importance = self._compute_importance_from_sources(features)

        return FusedFeatures(
            fused_vector=fused,
            feature_importance=importance,
            source_contributions=contributions,
            dimension_reduction_applied=False,
            n_original_features=len(fused),
            n_fused_features=len(fused),
            fusion_method="concatenation",
        )

    def fuse_weighted_sum(
        self,
        features: Dict[str, np.ndarray],
        weights: Optional[Dict[str, float]] = None
    ) -> FusedFeatures:
        """Weighted sum fusion with dimension matching."""
        if weights is None:
            weights = {k: 1.0 / len(features) for k in features}

        # Normalize weights
        total = sum(weights.values())
        weights = {k: v / total for k, v in weights.items()}

        fused = None
        contributions = {}

        for source, vec in features.items():
            flat = vec.flatten()
            weight = weights.get(source, 0.0)

            if fused is None:
                fused = np.zeros_like(flat)
            elif len(flat) != len(fused):
                # Pad or truncate to match dimensions
                if len(flat) < len(fused):
                    flat = np.pad(flat, (0, len(fused) - len(flat)))
                else:
                    flat = flat[:len(fused)]

            fused += weight * flat
            contributions[source] = weight

        importance = self._compute_importance_from_weights(weights, features)

        return FusedFeatures(
            fused_vector=fused,
            feature_importance=importance,
            source_contributions=contributions,
            dimension_reduction_applied=False,
            n_original_features=sum(v.flatten().shape[0] for v in features.values()),
            n_fused_features=len(fused),
            fusion_method="weighted_sum",
        )

    def fuse_attention(
        self,
        features: Dict[str, np.ndarray],
        query_vector: Optional[np.ndarray] = None
    ) -> FusedFeatures:
        """Attention-based fusion with dynamic importance weighting."""
        vectors = []
        source_names = []
        dim = None

        for source, vec in features.items():
            flat = vec.flatten()
            if dim is None:
                dim = len(flat)
            elif len(flat) != dim:
                if len(flat) < dim:
                    flat = np.pad(flat, (0, dim - len(flat)))
                else:
                    flat = flat[:dim]

            vectors.append(flat)
            source_names.append(source)

        if not vectors:
            raise ValueError("No features to fuse")

        feature_matrix = np.stack(vectors)

        # Compute attention scores
        if query_vector is not None:
            query = query_vector.flatten()
            if len(query) != dim:
                query = query[:dim] if len(query) > dim else np.pad(query, (0, dim - len(query)))

            scores = feature_matrix @ query
        else:
            # Self-attention: each source attends to all others
            scores = feature_matrix.mean(axis=0)
            scores = feature_matrix @ scores

        # Softmax normalization
        scores = np.exp(scores - scores.max())
        attention_weights = scores / scores.sum()

        # Weighted fusion
        fused = np.sum(feature_matrix * attention_weights[:, np.newaxis], axis=0)

        self._attention_weights = dict(zip(source_names, attention_weights.tolist()))

        contributions = dict(zip(source_names, attention_weights.tolist()))
        importance = self._compute_importance_from_weights(contributions, features)

        return FusedFeatures(
            fused_vector=fused,
            feature_importance=importance,
            source_contributions=contributions,
            dimension_reduction_applied=False,
            n_original_features=feature_matrix.size,
            n_fused_features=len(fused),
            fusion_method="attention",
        )

    def reduce_dimensions(
        self,
        features: np.ndarray,
        n_components: Optional[int] = None
    ) -> Tuple[np.ndarray, Optional[np.ndarray]]:
        """
        Apply PCA dimension reduction.

        Args:
            features: Feature matrix
            n_components: Number of components

        Returns:
            Tuple[np.ndarray, Optional[np.ndarray]]: Reduced features and components
        """
        from sklearn.decomposition import PCA

        if n_components is None:
            n_components = min(64, features.shape[1])

        if self._pca_components is None:
            pca = PCA(n_components=n_components)
            reduced = pca.fit_transform(features)
            self._pca_components = pca.components_
        else:
            reduced = features @ self._pca_components.T

        return reduced, self._pca_components

    def _compute_importance_from_sources(
        self,
        features: Dict[str, np.ndarray]
    ) -> Dict[str, float]:
        """Compute feature importance from source statistics."""
        importance = {}
        for source, vec in features.items():
            flat = vec.flatten()
            # Use variance as importance indicator
            importance[source] = float(np.var(flat))
        total = sum(importance.values())
        if total > 0:
            importance = {k: v / total for k, v in importance.items()}
        return importance

    def _compute_importance_from_weights(
        self,
        weights: Dict[str, float],
        features: Dict[str, np.ndarray]
    ) -> Dict[str, float]:
        """Compute feature importance from source weights."""
        importance = {}
        for source in features:
            importance[source] = weights.get(source, 0.0)
        return importance

    def fuse(
        self,
        features: Dict[str, np.ndarray],
        weights: Optional[Dict[str, float]] = None,
        reduce: bool = False,
        n_components: Optional[int] = None
    ) -> FusedFeatures:
        """
        Fuse features from multiple sources.

        Args:
            features: Dictionary of feature arrays by source
            weights: Optional fusion weights
            reduce: Whether to apply dimension reduction
            n_components: Number of components for reduction

        Returns:
            FusedFeatures: Fused feature vector
        """
        if self.method == "concatenation":
            result = self.fuse_concatenation(features)
        elif self.method == "weighted_sum":
            result = self.fuse_weighted_sum(features, weights)
        elif self.method == "attention":
            result = self.fuse_attention(features)
        else:
            logger.warning(f"Unknown fusion method: {self.method}, using concatenation")
            result = self.fuse_concatenation(features)

        if reduce and len(result.fused_vector) > (n_components or 64):
            reduced, _ = self.reduce_dimensions(
                result.fused_vector.reshape(1, -1),
                n_components
            )
            result.fused_vector = reduced.flatten()
            result.dimension_reduction_applied = True
            result.n_fused_features = len(result.fused_vector)

        return result
