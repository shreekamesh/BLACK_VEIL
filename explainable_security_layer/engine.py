"""
BLACK VEIL V5 — Explainable Security Layer
3-level explainable AI (XAI) for security decisions:
1. Local Explanation: per-decision feature importance
2. Global Explanation: model behavior overview
3. Counterfactual Explanation: what-if scenarios
"""
import math
import random
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional

from utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class LocalExplanation:
    """Per-decision explanation"""
    decision_id: str
    decision: str
    confidence: float
    feature_contributions: dict[str, float]  # feature -> contribution
    top_factors: list[dict[str, Any]]
    similar_past_events: int
    timestamp: str


@dataclass
class GlobalExplanation:
    """Model-level explanation"""
    model_name: str
    top_features: list[dict[str, Any]]
    class_statistics: dict[str, Any]
    confidence_calibration: dict[str, float]


@dataclass
class CounterfactualExplanation:
    """What-if explanation"""
    original_decision: str
    target_decision: str
    minimal_changes: list[dict[str, Any]]
    change_distance: float
    feasibility: float


class XAIEngine:
    """
    3-Level Explainable AI Engine for security decisions.
    
    Level 1: Local — SHAP-style feature importance per decision
    Level 2: Global — Model behavior and feature overview
    Level 3: Counterfactual — What-if scenario analysis
    """

    def __init__(self):
        self._local_history: list[LocalExplanation] = []
        logger.info("XAI Engine initialized")

    def generate_local_explanation(
        self,
        decision_id: str,
        decision: str,
        confidence: float,
        feature_values: dict[str, float],
        baseline_values: Optional[dict[str, float]] = None,
        similar_past: int = 0,
    ) -> LocalExplanation:
        """
        Generate local (per-decision) explanation using feature contribution analysis.
        
        φⱼ(f) = Σₛ⊆F\{j} [|s|!(|F|-|s|-1)!/|F|!] × [fₓ(S∪{j}) - fₓ(S)]
        """
        baseline = baseline_values or {}
        contributions = {}
        all_features = set(feature_values.keys()) | set(baseline.keys())

        for feature in all_features:
            current_val = feature_values.get(feature, 0)
            base_val = baseline.get(feature, 0)

            # Contribution: difference weighted by deviation from baseline
            if abs(base_val) > 0.001:
                deviation = (current_val - base_val) / max(0.001, abs(base_val))
            else:
                deviation = current_val

            # Normalized contribution (-1 to 1)
            contribution = math.tanh(deviation * confidence)
            contributions[feature] = round(contribution, 4)

        # Top factors (sorted by absolute contribution)
        top_factors = sorted(
            [{"feature": k, "contribution": v} for k, v in contributions.items()],
            key=lambda x: abs(x["contribution"]),
            reverse=True,
        )[:5]

        # Build natural language explanation lines
        explanation_parts = [
            f"Decision: {decision} (confidence: {confidence:.0%})",
            "Contributing Factors:",
        ]
        for factor in top_factors:
            direction = "increased" if factor["contribution"] > 0 else "decreased"
            explanation_parts.append(
                f"  • {factor['feature']} {direction} confidence by {abs(factor['contribution']):.1%}"
            )
        if similar_past > 0:
            explanation_parts.append(
                f"  • Similar to {similar_past} past cases"
            )

        explanation = XAIEngine._build_summary(decision, top_factors, similar_past)

        result = LocalExplanation(
            decision_id=decision_id,
            decision=decision,
            confidence=confidence,
            feature_contributions=contributions,
            top_factors=top_factors,
            similar_past_events=similar_past,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

        self._local_history.append(result)
        return result

    def generate_global_explanation(
        self,
        model_name: str,
        feature_importance: dict[str, float],
        decision_history: list[LocalExplanation],
        num_features: int = 5,
    ) -> GlobalExplanation:
        """
        Generate global (model-level) explanation of overall behavior.
        """
        total = len(decision_history)

        # Top features by average absolute contribution
        feature_scores: dict[str, float] = {}
        for explanation in decision_history:
            for factor in explanation.top_factors:
                feat = factor["feature"]
                feature_scores[feat] = feature_scores.get(feat, 0) + abs(factor["contribution"])

        top_features = sorted(
            [{"feature": k, "avg_importance": round(v / max(1, total), 4)}
             for k, v in feature_scores.items()],
            key=lambda x: x["avg_importance"],
            reverse=True,
        )[:num_features]

        # Per-class statistics
        class_stats: dict[str, dict[str, Any]] = {}
        for explanation in decision_history:
            decision = explanation.decision
            if decision not in class_stats:
                class_stats[decision] = {
                    "count": 0,
                    "avg_confidence": 0.0,
                    "total_confidences": 0.0,
                }
            class_stats[decision]["count"] += 1
            class_stats[decision]["total_confidences"] += explanation.confidence

        for decision, stats in class_stats.items():
            stats["avg_confidence"] = round(
                stats["total_confidences"] / max(1, stats["count"]), 4
            )
            del stats["total_confidences"]

        return GlobalExplanation(
            model_name=model_name,
            top_features=top_features,
            class_statistics=class_stats,
            confidence_calibration={
                "ece": round(self._expected_calibration_error(decision_history), 4),
                "overall_avg_conf": round(
                    sum(e.confidence for e in decision_history) / max(1, total), 4
                ),
            },
        )

    def generate_counterfactual(
        self,
        original_decision: str,
        target_decision: str,
        feature_values: dict[str, float],
        feature_ranges: dict[str, tuple[float, float]],
        num_changes: int = 3,
    ) -> CounterfactualExplanation:
        """
        Generate counterfactual explanation: minimal feature changes to flip decision.
        """
        changes = []
        total_distance = 0.0

        # Sort features by how close they are to target range
        scored_features: list[tuple[str, float]] = []
        for feature, (low, high) in feature_ranges.items():
            current = feature_values.get(feature, 0)
            if current < low:
                distance = (low - current) / max(0.001, high - low)
                target_val = low
            elif current > high:
                distance = (current - high) / max(0.001, high - low)
                target_val = high
            else:
                distance = 0.0
                target_val = current

            scored_features.append((feature, distance))

        # Pick features requiring minimal change
        scored_features.sort(key=lambda x: x[1])
        for i in range(min(num_changes, len(scored_features))):
            feature, distance = scored_features[i]
            if distance > 0:
                changes.append({
                    "feature": feature,
                    "from": feature_values.get(feature, 0),
                    "to": target_val if feature in feature_ranges else feature_values.get(feature, 0),
                    "change_magnitude": round(distance, 4),
                })
                total_distance += distance

        # Feasibility: how feasible is the change
        max_possible = sum(
            min(1.0, abs(feature_ranges.get(f, (0, 1))[1] - feature_ranges.get(f, (0, 1))[0]))
            for f in feature_values
        )
        feasibility = 1.0 - (total_distance / max(1.0, max_possible))

        return CounterfactualExplanation(
            original_decision=original_decision,
            target_decision=target_decision,
            minimal_changes=changes,
            change_distance=round(total_distance, 4),
            feasibility=round(min(1.0, feasibility * 2), 4),
        )

    def get_recent_explanations(self, limit: int = 10) -> list[LocalExplanation]:
        """Get recent local explanations"""
        return self._local_history[-limit:]

    def get_state_summary(self) -> dict[str, Any]:
        """Get summary of XAI Engine state"""
        return {
            "total_explanations": len(self._local_history),
            "decisions": dict(
                (e.decision, sum(1 for x in self._local_history if x.decision == e.decision))
                for e in self._local_history[-100:]
            ),
        }

    @staticmethod
    def _expected_calibration_error(explanations: list[LocalExplanation],
                                    num_bins: int = 10) -> float:
        """Compute Expected Calibration Error (ECE)"""
        if not explanations:
            return 0.0

        bin_edges = [i / num_bins for i in range(num_bins + 1)]
        ece = 0.0

        for i in range(num_bins):
            bin_examples = [
                e for e in explanations
                if bin_edges[i] <= e.confidence < bin_edges[i + 1]
            ]
            if not bin_examples:
                continue

            avg_confidence = sum(e.confidence for e in bin_examples) / len(bin_examples)
            # Approximate accuracy as confidence (in absence of ground truth)
            ece += (len(bin_examples) / len(explanations)) * abs(avg_confidence - 1.0)

        return ece

    @staticmethod
    def _build_summary(decision: str, top_factors: list[dict],
                       similar_past: int) -> str:
        """Build a natural-language summary"""
        if not top_factors:
            return f"Decision: {decision} — No contributing factors identified."

        main = f"{top_factors[0]['feature']} (primary contributor)"
        if similar_past > 0:
            return (
                f"Decision reached based on {main} "
                f"with {len(top_factors)} total factors. "
                f"Similar to {similar_past} past events."
            )
        return f"Decision reached based on {main} with {len(top_factors)} total factors."

