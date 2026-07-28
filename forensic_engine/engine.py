"""
BLACK VEIL V5 — Forensic Engine
Attack timeline reconstruction, IOC extraction, evidence correlation,
and intelligence generation from forensic evidence (Algorithm 24)
"""
import uuid
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional

from utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class ForensicEvent:
    """A forensic evidence event"""
    event_id: str
    event_type: str               # TIMELINE_RECONSTRUCTION, IOC_EXTRACTION, PATTERN_MATCH
    source: str                   # Engine that generated this
    severity: str                 # INFO, LOW, MEDIUM, HIGH, CRITICAL
    ioc_list: list[str] = field(default_factory=list)
    evidence: dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class AttackTimeline:
    """Reconstructed attack timeline entry"""
    step: int
    timestamp: str
    event_type: str
    description: str
    confidence: float
    source: str


@dataclass
class IntelligenceReport:
    """Generated intelligence from forensic analysis"""
    report_id: str
    attack_patterns: list[dict[str, Any]]
    iocs: list[str]
    mitre_mappings: list[dict[str, str]]
    severity: str
    summary: str


class ForensicEngine:
    """
    Forensic Intelligence Engine implementing Algorithm 24.
    
    Extracts actionable intelligence from forensic evidence:
    - Attack timeline reconstruction
    - Indicator of Compromise (IoC) extraction
    - Cross-reference with threat intelligence
    - Attack pattern identification (MITRE ATT&CK mapping)
    - Confidence-scored intelligence generation
    """

    def __init__(self):
        self._events: list[ForensicEvent] = []
        self._intelligence_reports: list[IntelligenceReport] = []

        # Known patterns for matching
        self._known_attack_patterns: dict[str, list[str]] = {
            "SQL_INJECTION": ["' OR '1'='1", "UNION SELECT", "DROP TABLE"],
            "XSS": ["<script>", "onerror=", "javascript:"],
            "PORT_SCAN": ["SYN flood", "port sweep", "service discovery"],
            "BRUTE_FORCE": ["multiple auth failures", "credential stuffing"],
            "RANSOMWARE": ["file encryption", "ransom note", "shadow copy delete"],
        }

        # MITRE ATT&CK mappings
        self._mitre_mapping: dict[str, tuple[str, str]] = {
            "SQL_INJECTION": ("T1190", "Initial Access"),
            "XSS": ("T1059.007", "Execution"),
            "PORT_SCAN": ("T1046", "Discovery"),
            "BRUTE_FORCE": ("T1110", "Credential Access"),
            "RANSOMWARE": ("T1486", "Impact"),
        }

        logger.info("Forensic Engine initialized")

    def ingest_event(
        self,
        event_type: str,
        source: str,
        severity: str = "INFO",
        evidence: Optional[dict[str, Any]] = None,
    ) -> ForensicEvent:
        """Ingest a forensic event for analysis"""
        event = ForensicEvent(
            event_id=str(uuid.uuid4()),
            event_type=event_type,
            source=source,
            severity=severity,
            evidence=evidence or {},
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

        # Extract IOCs from evidence
        event.ioc_list = self._extract_iocs(event.evidence)

        self._events.append(event)
        logger.info(
            f"Forensic event ingested: type={event_type}, source={source}, severity={severity}"
        )

        return event

    def reconstruct_timeline(
        self,
        events: Optional[list[ForensicEvent]] = None,
    ) -> list[AttackTimeline]:
        """
        Reconstruct attack timeline from forensic events (Algorithm 9).
        
        Timeline = {(e₁, t₁), (e₂, t₂), ..., (eₙ, tₙ)}
        P(Chain | Events) = Πᵢ P(eᵢ | chain) × P(chain transition)
        """
        source_events = events or self._events
        if not source_events:
            return []

        # Sort by timestamp
        sorted_events = sorted(
            source_events,
            key=lambda e: e.timestamp,
        )

        timeline = []
        kill_chain_order = ["reconnaissance", "weaponization", "delivery",
                            "exploitation", "installation", "command_control",
                            "actions_objectives"]

        for i, event in enumerate(sorted_events):
            # Map event type to kill chain phase
            phase = self._map_to_kill_chain(event.event_type, i, len(sorted_events))

            # Confidence decreases with distance from confirmed events
            confidence = max(0.3, 1.0 - (i / max(1, len(sorted_events))) * 0.5)

            timeline.append(AttackTimeline(
                step=i + 1,
                timestamp=event.timestamp,
                event_type=event.event_type,
                description=f"Step {i + 1}: {event.source} — {event.event_type}",
                confidence=round(confidence, 2),
                source=event.source,
            ))

        return timeline

    def generate_intelligence_report(
        self,
        events: Optional[list[ForensicEvent]] = None,
    ) -> IntelligenceReport:
        """
        Generate actionable intelligence from forensic evidence (Algorithm 24).
        """
        source_events = events or self._events
        report_id = str(uuid.uuid4())

        # Collect all IOCs
        all_iocs: set[str] = set()
        for event in source_events:
            all_iocs.update(event.ioc_list)

        # Identify attack patterns
        attack_patterns: list[dict[str, Any]] = []
        for pattern_name, indicators in self._known_attack_patterns.items():
            matches = [
                ioc for ioc in all_iocs
                if any(ind.lower() in ioc.lower() for ind in indicators)
            ]
            if matches:
                attack_patterns.append({
                    "pattern": pattern_name,
                    "confidence": len(matches) / max(1, len(indicators)),
                    "matched_indicators": matches,
                    "mitre_id": self._mitre_mapping.get(pattern_name, ("UNKNOWN", "Unknown"))[0],
                    "mitre_tactic": self._mitre_mapping.get(pattern_name, ("UNKNOWN", "Unknown"))[1],
                })

        # Determine overall severity
        severity = self._determine_severity(source_events, attack_patterns)

        # MITRE mappings
        mitre_mappings = [
            {"technique_id": mid, "tactic": tactic}
            for mid, tactic in self._mitre_mapping.values()
        ]

        # Summary
        summary = (
            f"Intelligence Report: {len(source_events)} events analyzed, "
            f"{len(all_iocs)} IOCs extracted, "
            f"{len(attack_patterns)} attack patterns identified. "
            f"Overall severity: {severity}."
        )

        report = IntelligenceReport(
            report_id=report_id,
            attack_patterns=attack_patterns,
            iocs=list(all_iocs),
            mitre_mappings=mitre_mappings,
            severity=severity,
            summary=summary,
        )

        self._intelligence_reports.append(report)

        logger.info(
            f"Intelligence report generated: {report_id[:8]}... "
            f"(patterns={len(attack_patterns)}, iocs={len(all_iocs)})"
        )

        return report

    def _extract_iocs(self, evidence: dict[str, Any]) -> list[str]:
        """Extract Indicators of Compromise from evidence"""
        iocs: list[str] = []

        # IP addresses
        ip_fields = ["source_ip", "destination_ip", "src_ip", "dst_ip", "ip_address"]
        for field in ip_fields:
            value = evidence.get(field)
            if value and isinstance(value, str):
                iocs.append(f"IP:{value}")

        # Hash values
        hash_fields = ["file_hash", "payload_hash", "md5", "sha1", "sha256"]
        for field in hash_fields:
            value = evidence.get(field)
            if value and isinstance(value, str):
                iocs.append(f"HASH:{value}")

        # Domain names
        domain_fields = ["domain", "hostname", "url", "fqdn"]
        for field in domain_fields:
            value = evidence.get(field)
            if value and isinstance(value, str):
                iocs.append(f"DOMAIN:{value}")

        # File paths
        file_fields = ["file_path", "process_path", "target_file"]
        for field in file_fields:
            value = evidence.get(field)
            if value and isinstance(value, str):
                iocs.append(f"FILE:{value}")

        return iocs

    def _map_to_kill_chain(self, event_type: str, index: int,
                            total: int) -> str:
        """Map event type/index to cyber kill chain phase"""
        phase_map = {
            "port_scan": "reconnaissance",
            "vulnerability_scan": "reconnaissance",
            "phishing": "delivery",
            "exploit": "exploitation",
            "malware": "installation",
            "c2_beacon": "command_control",
            "data_exfil": "actions_objectives",
            "ransomware": "actions_objectives",
        }

        # Direct mapping
        for key, phase in phase_map.items():
            if key in event_type.lower():
                return phase

        # Position-based fallback
        phases = ["reconnaissance", "weaponization", "delivery",
                  "exploitation", "installation", "command_control",
                  "actions_objectives"]
        position = min(len(phases) - 1, int((index / max(1, total)) * len(phases)))
        return phases[position]

    @staticmethod
    def _determine_severity(
        events: list[ForensicEvent],
        patterns: list[dict[str, Any]],
    ) -> str:
        """Determine overall severity from events and patterns"""
        severity_map = {"INFO": 0, "LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}
        reverse_map = {0: "INFO", 1: "LOW", 2: "MEDIUM", 3: "HIGH", 4: "CRITICAL"}

        if events:
            max_sev = max(severity_map.get(e.severity, 0) for e in events)
        else:
            max_sev = 0

        # Boost severity based on pattern matches
        for p in patterns:
            if p.get("confidence", 0) > 0.7:
                max_sev = min(4, max_sev + 1)

        return reverse_map.get(max_sev, "MEDIUM")

    def get_state_summary(self) -> dict[str, Any]:
        """Get summary of Forensic Engine state"""
        return {
            "total_events": len(self._events),
            "total_reports": len(self._intelligence_reports),
            "event_types": dict(
                (t, sum(1 for e in self._events if e.event_type == t))
                for t in set(e.event_type for e in self._events)
            ),
            "severity_distribution": dict(
                (s, sum(1 for e in self._events if e.severity == s))
                for s in set(e.severity for e in self._events)
            ),
        }

