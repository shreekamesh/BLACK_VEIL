"""
BLACK VEIL V5 — Report Engine
Comprehensive security report generation with trust, threat, deception, and system summaries
"""
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional

from utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class SecurityReport:
    """A comprehensive security report"""
    report_id: str
    report_type: str              # TRUST, THREAT, DECEPTION, SYSTEM, COMPREHENSIVE
    generated_at: str
    timeframe_start: str
    timeframe_end: str
    summary: dict[str, Any]
    details: dict[str, Any]
    recommendations: list[str] = field(default_factory=list)


class ReportEngine:
    """
    Report Engine for generating comprehensive security reports.
    
    Generates reports for:
    - Trust score summaries and trends
    - Threat event analysis
    - Deployment effectiveness
    - System health and status
    - Comprehensive security posture
    """

    def __init__(self):
        self._reports: list[SecurityReport] = []
        logger.info("Report Engine initialized")

    def generate_trust_report(
        self,
        trust_scores: dict[str, float],
        trust_history: Optional[dict[str, list[float]]] = None,
        timeframe_hours: int = 24,
    ) -> SecurityReport:
        """Generate a trust score summary report"""
        report_id = f"TR-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
        now = datetime.now(timezone.utc)

        avg_trust = sum(trust_scores.values()) / max(1, len(trust_scores))
        min_trust = min(trust_scores.values()) if trust_scores else 0
        max_trust = max(trust_scores.values()) if trust_scores else 0

        # Trend analysis
        trends = {}
        if trust_history:
            for domain, history in trust_history.items():
                if len(history) >= 2:
                    trend = (history[-1] - history[0]) / max(1, len(history))
                    trends[domain] = {
                        "direction": "improving" if trend > 0 else "declining",
                        "rate": round(abs(trend), 2),
                    }

        summary = {
            "average_trust": round(avg_trust, 2),
            "minimum_trust": round(min_trust, 2),
            "maximum_trust": round(max_trust, 2),
            "domains_monitored": list(trust_scores.keys()),
            "trends": trends,
        }

        details = {
            "per_domain": trust_scores,
            "history_summary": {
                d: {"mean": round(sum(h[-20:]) / max(1, len(h[-20:])), 2),
                    "last": h[-1] if h else 0}
                for d, h in (trust_history or {}).items()
            },
        }

        recommendations = []
        if avg_trust < 50:
            recommendations.append("CRITICAL: Average trust below 50 — immediate investigation required")
        elif avg_trust < 70:
            recommendations.append("WARNING: Average trust below 70 — review high-risk domains")
        if trends:
            declining = [d for d, t in trends.items() if t["direction"] == "declining"]
            if declining:
                recommendations.append(f"Declining trust in: {', '.join(declining)}")

        report = SecurityReport(
            report_id=report_id,
            report_type="TRUST",
            generated_at=now.isoformat(),
            timeframe_start=now.isoformat(),
            timeframe_end=now.isoformat(),
            summary=summary,
            details=details,
            recommendations=recommendations,
        )

        self._reports.append(report)
        logger.info(f"Trust report generated: {report_id}")
        return report

    def generate_threat_report(
        self,
        threat_events: list[dict[str, Any]],
        timeframe_hours: int = 24,
    ) -> SecurityReport:
        """Generate a threat event analysis report"""
        report_id = f"THR-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
        now = datetime.now(timezone.utc)

        # Analyze threats
        severity_counts: dict[str, int] = {}
        type_counts: dict[str, int] = {}
        total = len(threat_events)

        for event in threat_events:
            sev = event.get("severity", "UNKNOWN")
            severity_counts[sev] = severity_counts.get(sev, 0) + 1
            etype = event.get("threat_type", "UNKNOWN")
            type_counts[etype] = type_counts.get(etype, 0) + 1

        summary = {
            "total_events": total,
            "by_severity": severity_counts,
            "by_type": type_counts,
            "critical_count": severity_counts.get("CRITICAL", 0),
            "high_count": severity_counts.get("HIGH", 0),
        }

        details = {
            "events": threat_events[-50:],  # Last 50
            "severity_breakdown": severity_counts,
            "type_breakdown": type_counts,
        }

        recommendations = []
        if summary["critical_count"] > 0:
            recommendations.append(
                f"URGENT: {summary['critical_count']} critical threats require immediate action"
            )
        if summary["high_count"] > 5:
            recommendations.append(
                f"REVIEW: {summary['high_count']} high-severity threats in timeframe"
            )
        if total > 100:
            recommendations.append(f"ALERT: High threat volume ({total} events) — consider scaling resources")

        report = SecurityReport(
            report_id=report_id,
            report_type="THREAT",
            generated_at=now.isoformat(),
            timeframe_start=now.isoformat(),
            timeframe_end=now.isoformat(),
            summary=summary,
            details=details,
            recommendations=recommendations,
        )

        self._reports.append(report)
        logger.info(f"Threat report generated: {report_id}")
        return report

    def generate_deception_report(
        self,
        deception_events: list[dict[str, Any]],
        credentials: list[dict[str, Any]],
        timeframe_hours: int = 24,
    ) -> SecurityReport:
        """Generate a deception effectiveness report"""
        report_id = f"DEC-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
        now = datetime.now(timezone.utc)

        active_deceptions = [d for d in deception_events if d.get("status") == "ACTIVE"]
        triggered = [d for d in deception_events if d.get("status") == "TRIGGERED"]
        active_creds = [c for c in credentials if c.get("status") == "ACTIVE"]

        total_interactions = sum(d.get("interaction_count", 0) for d in deception_events)

        summary = {
            "active_deceptions": len(active_deceptions),
            "triggered_deceptions": len(triggered),
            "active_credentials": len(active_creds),
            "total_interactions": total_interactions,
            "avg_effectiveness": round(
                sum(d.get("effectiveness", 0) or 0 for d in deception_events)
                / max(1, len(deception_events)), 4
            ),
        }

        details = {
            "deceptions": deception_events,
            "credentials": credentials,
        }

        recommendations = []
        if summary["triggered_deceptions"] > 0:
            recommendations.append(
                f"ACTION: {summary['triggered_deceptions']} deceptions triggered — review attacker interactions"
            )
        if summary["avg_effectiveness"] < 0.5:
            recommendations.append("REVIEW: Deception effectiveness below 50% — consider strategy evolution")

        report = SecurityReport(
            report_id=report_id,
            report_type="DECEPTION",
            generated_at=now.isoformat(),
            timeframe_start=now.isoformat(),
            timeframe_end=now.isoformat(),
            summary=summary,
            details=details,
            recommendations=recommendations,
        )

        self._reports.append(report)
        logger.info(f"Deception report generated: {report_id}")
        return report

    def generate_comprehensive_report(
        self,
        trust_data: dict[str, Any],
        threat_data: dict[str, Any],
        deception_data: dict[str, Any],
        system_data: dict[str, Any],
    ) -> SecurityReport:
        """Generate a comprehensive security posture report"""
        report_id = f"COMP-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
        now = datetime.now(timezone.utc)

        summary = {
            "trust_summary": trust_data.get("summary", {}),
            "threat_summary": threat_data.get("summary", {}),
            "deception_summary": deception_data.get("summary", {}),
            "system_summary": system_data.get("summary", {}),
            "overall_health": self._calculate_overall_health(
                trust_data, threat_data, system_data
            ),
        }

        details = {
            "trust": trust_data,
            "threats": threat_data,
            "deception": deception_data,
            "system": system_data,
        }

        recommendations = self._generate_recommendations(
            trust_data, threat_data, deception_data, system_data
        )

        report = SecurityReport(
            report_id=report_id,
            report_type="COMPREHENSIVE",
            generated_at=now.isoformat(),
            timeframe_start=now.isoformat(),
            timeframe_end=now.isoformat(),
            summary=summary,
            details=details,
            recommendations=recommendations,
        )

        self._reports.append(report)
        logger.info(f"Comprehensive report generated: {report_id}")
        return report

    def get_recent_reports(self, report_type: Optional[str] = None,
                           limit: int = 10) -> list[SecurityReport]:
        """Get recent reports, optionally filtered by type"""
        filtered = self._reports
        if report_type:
            filtered = [r for r in filtered if r.report_type == report_type]
        return filtered[-limit:]

    @staticmethod
    def _calculate_overall_health(
        trust_data: dict[str, Any],
        threat_data: dict[str, Any],
        system_data: dict[str, Any],
    ) -> str:
        """Calculate overall security health"""
        trust_summary = trust_data.get("summary", {})
        threat_summary = threat_data.get("summary", {})

        avg_trust = trust_summary.get("average_trust", 50)
        critical_threats = threat_summary.get("critical_count", 0)
        high_threats = threat_summary.get("high_count", 0)

        if avg_trust < 40 or critical_threats > 3:
            return "CRITICAL"
        elif avg_trust < 60 or high_threats > 10:
            return "WARNING"
        elif avg_trust < 80:
            return "FAIR"
        return "GOOD"

    @staticmethod
    def _generate_recommendations(
        trust_data: dict[str, Any],
        threat_data: dict[str, Any],
        deception_data: dict[str, Any],
        system_data: dict[str, Any],
    ) -> list[str]:
        """Generate recommendations from all data sources"""
        recommendations = []

        trust_summary = trust_data.get("summary", {})
        threat_summary = threat_data.get("summary", {})
        deception_summary = deception_data.get("summary", {})

        # Trust-based
        avg_trust = trust_summary.get("average_trust", 50)
        if avg_trust < 50:
            recommendations.append("CRITICAL: Overall trust score below 50 — immediate action required")
        elif avg_trust < 70:
            recommendations.append("WARNING: Trust score below 70 — review agent configurations")

        # Threat-based
        critical = threat_summary.get("critical_count", 0)
        high = threat_summary.get("high_count", 0)
        if critical > 0:
            recommendations.append(f"URGENT: {critical} critical threats detected")
        if high > 5:
            recommendations.append(f"REVIEW: {high} high-severity threats require analysis")

        # Deception-based
        triggered = deception_summary.get("triggered_deceptions", 0)
        if triggered > 0:
            recommendations.append(f"INFO: {triggered} deceptions triggered — analyze attacker behavior")

        if not recommendations:
            recommendations.append("No critical issues detected — system operating normally")

        return recommendations

    def get_state_summary(self) -> dict[str, Any]:
        """Get summary of Report Engine state"""
        types = {}
        for r in self._reports:
            types[r.report_type] = types.get(r.report_type, 0) + 1
        return {
            "total_reports": len(self._reports),
            "by_type": types,
            "latest_report": self._reports[-1].report_id if self._reports else None,
        }
