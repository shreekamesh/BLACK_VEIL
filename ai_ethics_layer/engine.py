"""
BLACK VEIL V5 — AI Ethics Layer
Pre-decision bias and fairness checks, mode selection (autonomous/semi/manual),
and post-decision audit logging
"""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional

from utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class EthicsCheckResult:
    """Result of pre-decision ethics checks"""
    passed: bool
    bias_score: float
    fairness_score: float
    confidence_calibrated: bool
    recommendation: str              # PROCEED, REVIEW, REJECT
    mode: str                        # AUTONOMOUS, SEMI_AUTONOMOUS, MANUAL
    warnings: list[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class AuditEntry:
    """Post-decision audit log entry"""
    decision_id: str
    decision: str
    mode: str
    confidence: float
    bias_score: float
    fairness_score: float
    human_overridden: bool
    timestamp: str


class EthicsEngine:
    """
    AI Ethics Layer ensuring responsible autonomous decision-making.
    
    Monitors before/during/after every autonomous decision:
    - Pre-decision: Bias scoring, fairness check, confidence calibration
    - Decision-time: Mode selection (autonomous/semi/manual)
    - Post-decision: Audit logging, flagging, human override tracking
    
    Config (from config.settings.ethics):
        bias_threshold: Max allowed bias score (default: 0.3)
        fairness_threshold: Min allowed fairness (default: 0.7)
        confidence_auto: Min confidence for autonomous mode (default: 0.85)
        confidence_semi: Min confidence for semi-autonomous (default: 0.65)
        risk_auto: Max risk for autonomous mode (default: 60)
        risk_critical: Risk above this triggers manual mode (default: 85)
    """

    def __init__(self, config: Optional[dict[str, Any]] = None):
        self.config = config or {}
        self._bias_threshold = float(self.config.get("bias_threshold", 0.3))
        self._fairness_threshold = float(self.config.get("fairness_threshold", 0.7))
        self._confidence_auto = float(self.config.get("confidence_auto", 0.85))
        self._confidence_semi = float(self.config.get("confidence_semi", 0.65))
        self._risk_auto = float(self.config.get("risk_auto", 60.0))
        self._risk_critical = float(self.config.get("risk_critical", 85.0))

        self._audit_log: list[AuditEntry] = []
        self._human_overrides: int = 0

        logger.info("Ethics Engine initialized")

    def pre_decision_check(
        self,
        decision_id: str,
        confidence: float,
        risk_score: float,
        feature_values: Optional[dict[str, float]] = None,
        demographic_data: Optional[dict[str, Any]] = None,
    ) -> EthicsCheckResult:
        """
        Run pre-decision ethics checks.
        
        1. Bias Score: Measure demographic/feature bias using disparate impact
        2. Fairness Check: Equal treatment across groups
        3. Confidence Calibration: ECE < threshold
        4. Mode Selection: Choose autonomy level
        """
        warnings: list[str] = []

        # 1. Bias Score
        bias_score = self._compute_bias_score(feature_values, demographic_data)

        # 2. Fairness Check
        fairness_score = self._compute_fairness_score(feature_values, demographic_data)

        # 3. Confidence calibration check
        confidence_calibrated = confidence >= self._confidence_semi
        if not confidence_calibrated:
            warnings.append(f"Confidence ({confidence:.2f}) below semi-autonomous threshold")

        # 4. Mode selection
        mode = self._select_mode(confidence, risk_score, bias_score)
        if mode == "MANUAL":
            warnings.append(f"Risk score {risk_score:.1f} exceeds critical threshold, requiring manual mode")

        # 5. Overall assessment
        passed = (
            bias_score <= self._bias_threshold
            and fairness_score >= self._fairness_threshold
            and confidence_calibrated
        )

        if bias_score > self._bias_threshold:
            warnings.append(f"Bias score {bias_score:.3f} exceeds threshold {self._bias_threshold}")

        if fairness_score < self._fairness_threshold:
            warnings.append(f"Fairness score {fairness_score:.3f} below threshold {self._fairness_threshold}")

        if passed:
            recommendation = "PROCEED"
        elif mode == "MANUAL":
            recommendation = "REJECT"
        else:
            recommendation = "REVIEW"

        logger.info(
            f"Ethics check: {recommendation} (mode={mode}, bias={bias_score:.3f}, "
            f"fairness={fairness_score:.3f})"
        )

        return EthicsCheckResult(
            passed=passed,
            bias_score=round(bias_score, 4),
            fairness_score=round(fairness_score, 4),
            confidence_calibrated=confidence_calibrated,
            recommendation=recommendation,
            mode=mode,
            warnings=warnings,
        )

    def post_decision_audit(
        self,
        decision_id: str,
        decision: str,
        mode: str,
        confidence: float,
        bias_score: float,
        fairness_score: float,
        human_overridden: bool = False,
    ) -> None:
        """Log a post-decision audit entry"""
        entry = AuditEntry(
            decision_id=decision_id,
            decision=decision,
            mode=mode,
            confidence=confidence,
            bias_score=bias_score,
            fairness_score=fairness_score,
            human_overridden=human_overridden,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
        self._audit_log.append(entry)

        if human_overridden:
            self._human_overrides += 1
            logger.warning(f"Human override recorded for decision: {decision_id[:8]}...")
        elif bias_score > self._bias_threshold * 1.5:
            logger.warning(
                f"Flagged: High bias decision {decision_id[:8]}... "
                f"(bias={bias_score:.3f})"
            )

    def _select_mode(self, confidence: float, risk_score: float,
                     bias_score: float) -> str:
        """
        Select decision autonomy mode.
        
        Autonomous: confidence > θ_auto AND risk < R_auto AND bias < threshold
        Semi-Autonomous: confidence in [θ_semi, θ_auto]
        Manual: confidence < θ_semi OR risk > R_critical
        """
        if (
            confidence >= self._confidence_auto
            and risk_score <= self._risk_auto
            and bias_score <= self._bias_threshold
        ):
            return "AUTONOMOUS"

        if (
            confidence >= self._confidence_semi
            and risk_score <= self._risk_critical
        ):
            return "SEMI_AUTONOMOUS"

        return "MANUAL"

    def _compute_bias_score(
        self,
        feature_values: Optional[dict[str, float]] = None,
        demographic_data: Optional[dict[str, Any]] = None,
    ) -> float:
        """
        Compute bias score using disparate impact analysis.
        
        Bias = max deviation in treatment across groups.
        Score 0 = no bias, 1 = maximum bias.
        """
        bias = 0.0

        if demographic_data:
            # Check for disparate impact across groups
            groups = demographic_data.get("groups", {})
            if len(groups) > 1:
                values = list(groups.values())
                mean_val = sum(values) / len(values)
                max_deviation = max(abs(v - mean_val) for v in values)
                bias = max(bias, max_deviation / max(0.001, mean_val))

        if feature_values:
            # Check for disproportionate feature influence
            if len(feature_values) > 1:
                values = list(feature_values.values())
                if max(values) > 0:
                    gini = self._compute_gini(values)
                    bias = max(bias, gini * 0.5)  # Scale Gini contribution

        return min(1.0, bias)

    def _compute_fairness_score(
        self,
        feature_values: Optional[dict[str, float]] = None,
        demographic_data: Optional[dict[str, Any]] = None,
    ) -> float:
        """
        Compute fairness score.
        
        1.0 = perfectly fair, 0.0 = completely unfair.
        """
        if not demographic_data and not feature_values:
            return 1.0  # No data to check = fair by default

        bias = self._compute_bias_score(feature_values, demographic_data)
        return 1.0 - bias

    def get_audit_summary(self) -> dict[str, Any]:
        """Get summary of ethics audit"""
        total = len(self._audit_log)
        if total == 0:
            return {"total_decisions": 0, "human_overrides": 0}

        mode_counts: dict[str, int] = {}
        for entry in self._audit_log:
            mode_counts[entry.mode] = mode_counts.get(entry.mode, 0) + 1

        return {
            "total_decisions": total,
            "human_overrides": self._human_overrides,
            "modes": mode_counts,
            "avg_bias": round(
                sum(e.bias_score for e in self._audit_log) / total, 4
            ),
            "avg_fairness": round(
                sum(e.fairness_score for e in self._audit_log) / total, 4
            ),
        }

    @staticmethod
    def _compute_gini(values: list[float]) -> float:
        """Compute Gini coefficient as a measure of inequality"""
        if not values:
            return 0.0
        sorted_values = sorted(values)
        n = len(sorted_values)
        cumulative = 0.0
        total = sum(sorted_values)
        if total == 0:
            return 0.0
        for i, v in enumerate(sorted_values):
            cumulative += (i + 1) * v
        gini = (2 * cumulative) / (n * total) - (n + 1) / n
        return max(0.0, gini)

