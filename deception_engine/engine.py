"""
BLACK VEIL V5 — Deception Engine
Honeypot deployment, digital twins, fake credentials, and deception operations management
"""
import json
import random
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from utils.logger import get_logger

logger = get_logger(__name__)

# ── Service Templates for Honeypot Generation ─────────────────

SERVICE_TEMPLATES: dict[str, dict[str, Any]] = {
    "http": {
        "name": "HTTP",
        "port": 80,
        "banners": [
            "Apache/2.4.54 (Ubuntu) Server",
            "nginx/1.24.0",
            "Microsoft-IIS/10.0",
            "Apache/2.2.34 (CentOS)",
        ],
        "vulnerabilities": ["CVE-2021-41773", "CVE-2023-27522", "CVE-2022-22720"],
    },
    "https": {
        "name": "HTTPS",
        "port": 443,
        "banners": [
            "Apache/2.4.54 (Ubuntu) mod_ssl/2.4.54",
            "nginx/1.24.0 OpenSSL/3.0.7",
        ],
        "vulnerabilities": ["CVE-2022-0778", "CVE-2023-4807"],
    },
    "ssh": {
        "name": "SSH",
        "port": 22,
        "banners": [
            "OpenSSH_8.9p1 Ubuntu-3ubuntu0.1",
            "OpenSSH_7.9p1 Debian-10+deb10u2",
            "SSH-2.0-OpenSSH_9.0",
        ],
        "vulnerabilities": ["CVE-2023-38408", "CVE-2021-41617"],
    },
    "ftp": {
        "name": "FTP",
        "port": 21,
        "banners": [
            "vsftpd 3.0.5",
            "ProFTPD 1.3.7a Server",
            "FileZilla Server 1.5.1",
        ],
        "vulnerabilities": ["CVE-2023-27522", "CVE-2021-36159"],
    },
    "mysql": {
        "name": "MySQL",
        "port": 3306,
        "banners": ["MySQL 8.0.32", "MySQL 5.7.41", "MariaDB 10.11.2"],
        "vulnerabilities": ["CVE-2023-21971", "CVE-2022-21367"],
    },
    "postgresql": {
        "name": "PostgreSQL",
        "port": 5432,
        "banners": ["PostgreSQL 15.2", "PostgreSQL 14.7"],
        "vulnerabilities": ["CVE-2023-2454", "CVE-2022-2625"],
    },
    "rdp": {
        "name": "RDP",
        "port": 3389,
        "banners": ["Microsoft Terminal Server", "xrdp 0.9.21"],
        "vulnerabilities": ["CVE-2023-28257", "CVE-2022-21893"],
    },
    "smtp": {
        "name": "SMTP",
        "port": 25,
        "banners": ["Postfix 3.6.4", "Sendmail 8.17.1"],
        "vulnerabilities": ["CVE-2023-51764", "CVE-2022-30295"],
    },
    "dns": {
        "name": "DNS",
        "port": 53,
        "banners": ["BIND 9.18.12", "Unbound 1.17.0"],
        "vulnerabilities": ["CVE-2023-3341", "CVE-2022-2795"],
    },
    "redis": {
        "name": "Redis",
        "port": 6379,
        "banners": ["Redis 7.0.11", "Redis 6.2.12"],
        "vulnerabilities": ["CVE-2023-28856", "CVE-2022-0543"],
    },
}


@dataclass
class DeceptionService:
    """A service running on a honeypot"""
    name: str
    port: int
    banner: str
    vulnerabilities: list[str]


@dataclass
class Honeypot:
    """A deployed honeypot instance"""
    honeypot_id: str
    name: str
    ip_address: str
    services: list[DeceptionService]
    status: str                     # ACTIVE, TRIGGERED, COMPROMISED, EXPIRED
    realism: float                  # 0-1
    created_at: str
    expires_at: str
    interaction_count: int = 0
    attacker_data: list[dict] = field(default_factory=list)


class DeceptionEngine:
    """
    Deception Engine for deploying and managing honeypots, digital twins,
    and fake credentials.
    
    Implements:
    - Honeypot lifecycle (create, monitor, expire)
    - Digital twin creation from real assets
    - Fake data generation (users, files, credentials)
    - Interaction tracking and intelligence gathering
    """

    def __init__(self):
        self._honeypots: dict[str, Honeypot] = {}
        self._digital_twins: dict[str, dict[str, Any]] = {}
        self._fake_data_cache: dict[str, Any] = {}

        logger.info("Deception Engine initialized")

    # ── Honeypot Operations ──────────────────────────────────

    def create_honeypot(
        self,
        name: str,
        service_types: Optional[list[str]] = None,
        duration_hours: int = 24,
        realism: float = 0.85,
    ) -> Honeypot:
        """
        Create and deploy a new honeypot with realistic services.
        
        Args:
            name: Honeypot name
            service_types: Services to simulate (defaults to SSH, HTTP)
            duration_hours: Lifetime in hours
            realism: Realism level (0-1)
            
        Returns:
            Deployed Honeypot instance
        """
        honeypot_id = str(uuid.uuid4())
        service_types = service_types or ["ssh", "http"]
        now = datetime.now(timezone.utc)

        services = []
        for stype in service_types:
            template = SERVICE_TEMPLATES.get(stype)
            if template:
                services.append(DeceptionService(
                    name=template["name"],
                    port=template["port"],
                    banner=random.choice(template["banners"]),
                    vulnerabilities=random.sample(
                        template["vulnerabilities"],
                        k=min(len(template["vulnerabilities"]), 2),
                    ),
                ))

        honeypot = Honeypot(
            honeypot_id=honeypot_id,
            name=name,
            ip_address=f"10.0.{random.randint(1, 255)}.{random.randint(1, 255)}",
            services=services,
            status="ACTIVE",
            realism=min(1.0, max(0.0, realism)),
            created_at=now.isoformat(),
            expires_at=(now + timedelta(hours=duration_hours)).isoformat(),
        )

        self._honeypots[honeypot_id] = honeypot

        logger.info(
            f"Honeypot deployed: {name} ({honeypot_id[:8]}...) with {len(services)} services",
            extra={
                "extra": {
                    "honeypot_id": honeypot_id,
                    "services": [s.name for s in services],
                    "duration_hours": duration_hours,
                    "realism": realism,
                }
            },
        )

        return honeypot

    def record_interaction(
        self,
        honeypot_id: str,
        interaction: dict[str, Any],
    ) -> dict[str, Any]:
        """Record attacker interaction with a honeypot"""
        if honeypot_id not in self._honeypots:
            logger.warning(f"Unknown honeypot: {honeypot_id}")
            return {}

        honeypot = self._honeypots[honeypot_id]
        honeypot.interaction_count += 1

        enriched = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "honeypot": honeypot.name,
            "source_ip": interaction.get("source_ip", "unknown"),
            "type": interaction.get("type", "unknown"),
            "data": interaction,
        }
        honeypot.attacker_data.append(enriched)

        if interaction.get("type") in ("compromise", "exploit"):
            honeypot.status = "COMPROMISED"

        logger.info(
            f"Interaction #{honeypot.interaction_count} on {honeypot.name}: {interaction.get('type', 'unknown')}"
        )

        return enriched

    def expire_honeypot(self, honeypot_id: str) -> None:
        """Expire a honeypot"""
        if honeypot_id in self._honeypots:
            self._honeypots[honeypot_id].status = "EXPIRED"
            logger.info(f"Honeypot expired: {honeypot_id[:8]}...")

    # ── Digital Twin Operations ──────────────────────────────

    def create_digital_twin(
        self,
        asset_name: str,
        asset_data: dict[str, Any],
        duration_hours: int = 48,
    ) -> dict[str, Any]:
        """
        Create a digital twin (replica) of a real asset for deception.
        
        Args:
            asset_name: Name of the asset to replicate
            asset_data: Asset configuration and data blueprint
            duration_hours: Twin lifetime in hours
            
        Returns:
            Digital twin instance
        """
        twin_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)

        twin = {
            "id": twin_id,
            "name": f"{asset_name}_mirror",
            "target": asset_name,
            "status": "ACTIVE",
            "blueprint": asset_data,
            "created_at": now.isoformat(),
            "expires_at": (now + timedelta(hours=duration_hours)).isoformat(),
            "interactions": 0,
            "drift": 0.0,
        }

        self._digital_twins[twin_id] = twin

        logger.info(f"Digital twin created for {asset_name}: {twin_id[:8]}...")

        return twin

    def update_twin_drift(
        self,
        twin_id: str,
        actual_state: dict[str, Any],
    ) -> float:
        """
        Calculate and update digital twin drift from real asset state.
        """
        if twin_id not in self._digital_twins:
            return 1.0

        twin = self._digital_twins[twin_id]
        blueprint = twin.get("blueprint", {})

        # Calculate drift as normalized difference
        differences = 0
        total_keys = 0
        for key in set(list(blueprint.keys()) + list(actual_state.keys())):
            total_keys += 1
            if blueprint.get(key) != actual_state.get(key):
                differences += 1

        drift = differences / max(1, total_keys)
        twin["drift"] = drift

        return drift

    # ── Fake Data Generation ─────────────────────────────────

    def generate_fake_users(self, count: int = 10) -> list[dict[str, Any]]:
        """Generate fake user records for honeypot seeding"""
        first_names = ["admin", "root", "john", "jane", "bob", "alice", "david", "sarah"]
        last_names = ["smith", "jones", "admin", "brown", "wilson", "taylor", "davis"]

        users = []
        for i in range(count):
            users.append({
                "id": i + 1,
                "username": f"{random.choice(first_names)}_{random.randint(1, 999)}",
                "full_name": f"{random.choice(first_names).title()} {random.choice(last_names).title()}",
                "email": f"user{i}@internal-{random.choice(['corp', 'ent', 'labs'])}.com",
                "role": random.choice(["admin", "user", "operator", "viewer"]),
                "last_login": (datetime.now(timezone.utc) - timedelta(hours=random.randint(1, 720))).isoformat(),
                "failed_logins": random.randint(0, 5),
            })
        return users

    def generate_fake_files(self, count: int = 20) -> list[dict[str, Any]]:
        """Generate fake file records"""
        extensions = [".conf", ".xml", ".json", ".csv", ".log", ".txt", ".sql", ".yml"]
        directories = ["/etc", "/var/log", "/opt/app/config", "/home/user", "/data/backup"]

        files = []
        for i in range(count):
            ext = random.choice(extensions)
            files.append({
                "id": i + 1,
                "name": f"{random.choice(['config', 'app', 'data', 'backup', 'secret', 'passwd'])}{ext}",
                "path": f"{random.choice(directories)}/",
                "size": random.randint(100, 10_000_000),
                "modified": (datetime.now(timezone.utc) - timedelta(hours=random.randint(1, 8760))).isoformat(),
                "permissions": random.choice(["644", "755", "600", "400"]),
            })
        return files

    def generate_fake_database(self, record_count: int = 100) -> list[dict[str, Any]]:
        """Generate fake database records"""
        tables = ["users", "customers", "orders", "products", "transactions", "credentials"]
        records = []

        table = random.choice(tables)
        for i in range(min(record_count, 500)):
            records.append({
                "id": i + 1,
                "table": table,
                "data": {
                    "name": f"record_{i}",
                    "value": random.randint(1, 1000000),
                    "status": random.choice(["active", "inactive", "suspended", "pending"]),
                    "created": (datetime.now(timezone.utc) - timedelta(days=random.randint(1, 365))).isoformat(),
                },
            })
        return records

    # ── State Management ─────────────────────────────────────

    def get_honeypot(self, honeypot_id: str) -> Optional[Honeypot]:
        """Get a specific honeypot"""
        return self._honeypots.get(honeypot_id)

    def list_honeypots(self, status: Optional[str] = None) -> list[Honeypot]:
        """List honeypots, optionally filtered by status"""
        if status:
            return [h for h in self._honeypots.values() if h.status == status]
        return list(self._honeypots.values())

    def get_state_summary(self) -> dict[str, Any]:
        """Get summary of Deception Engine state"""
        active = [h for h in self._honeypots.values() if h.status == "ACTIVE"]
        compromised = [h for h in self._honeypots.values() if h.status == "COMPROMISED"]
        total_interactions = sum(h.interaction_count for h in self._honeypots.values())

        return {
            "total_honeypots": len(self._honeypots),
            "active_honeypots": len(active),
            "compromised_honeypots": len(compromised),
            "digital_twins": len(self._digital_twins),
            "total_interactions": total_interactions,
        }

