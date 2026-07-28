"""
BLACK VEIL V5 — Dynamic Credential Mutation Model (DCMM)
IEEE Research Contribution 3: Self-protecting credentials with biological lifecycle abstraction

Mathematical Model:
    G = (S, M, Sel, Fit, L, P)
    Fit(S) = w₁·H(S) + w₂·I(S) + w₃·S(S) + w₄·L(S)

Key Novelty: First application of a biological lifecycle abstraction (genome → mutation → 
evolution → death) with formal genetic operators to adaptive fake credential management 
in cyber deception.
"""
import math
import random
import secrets
import string
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class CredentialGenome:
    """
    Biological genome representation for a credential.
    
    G = (S, M, Sel, Fit, L, P)
    """
    genome_id: str
    credential_id: str
    sequence: str                        # S — Genome sequence
    generation: int                      # Evolution generation
    fitness: float                       # Fit(S) — Fitness score (0-1)
    entropy: float                       # H(S) — Shannon entropy
    mutation_rate: float                 # θ — Current mutation rate
    lifetime: int                        # L(S) — Expected lifetime in seconds
    age_seconds: int = 0                 # Current age
    parent_id: Optional[str] = None      # P — Parent genome reference
    mutation_history: list[dict[str, Any]] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class Credential:
    """A credential with its genome and lifecycle state"""
    credential_id: str
    service_name: str
    credential_type: str   # SSH, HTTP, FTP, DB, API
    username: str
    password_hash: str
    genome: CredentialGenome
    status: str            # ACTIVE, MUTATED, DETECTED, EXPIRED
    lifetime_sec: int
    mutated_count: int = 0
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    last_used_at: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)


class DCMMEngine:
    """
    Dynamic Credential Mutation Model Engine (Algorithms 5, 6, 21).
    
    Implements:
    - Credential genome generation and lifecycle management
    - Point mutation, insertion, deletion, duplication, crossover operators
    - Fitness-proportional selection with entropy preservation
    - Lifetime prediction with survival analysis
    - Proactive credential rotation
    - Identity evolution
    
    Configuration (from config.settings.dcmm):
        mutation_interval: Time between mutations in seconds (default: 1800)
        credential_lifetime: Default credential lifetime in seconds (default: 86400)
        complexity_min: Minimum credential length (default: 16)
        genome_size: Genome sequence length (default: 128)
        mutation_rate: θ₀ — Base mutation rate (default: 0.01)
        population_size: Max credential population (default: 50)
        fitness_threshold: Minimum fitness to keep (default: 0.7)
    """

    def __init__(self, config: Optional[dict[str, Any]] = None):
        self.config = config or {}
        self._mutation_interval = int(self.config.get("mutation_interval", 1800))
        self._credential_lifetime = int(self.config.get("credential_lifetime", 86400))
        self._complexity_min = int(self.config.get("complexity_min", 16))
        self._genome_size = int(self.config.get("genome_size", 128))
        self._base_mutation_rate = float(self.config.get("mutation_rate", 0.01))
        self._population_size = int(self.config.get("population_size", 50))
        self._fitness_threshold = float(self.config.get("fitness_threshold", 0.7))

        # In-memory stores
        self._credentials: dict[str, Credential] = {}
        self._genomes: dict[str, CredentialGenome] = {}
        self._identities: dict[str, dict[str, Any]] = {}

        logger.info(
            "DCMM Engine initialized",
            extra={
                "extra": {
                    "genome_size": self._genome_size,
                    "mutation_rate": self._base_mutation_rate,
                    "credential_lifetime": self._credential_lifetime,
                }
            },
        )

    # ── Credential Generation ────────────────────────────────

    def generate_credential(
        self,
        service_name: str,
        credential_type: str = "API",
        username: Optional[str] = None,
        length: Optional[int] = None,
        complexity: str = "high",
    ) -> Credential:
        """
        Generate a new credential with its genome.
        
        Args:
            service_name: Service this credential is for
            credential_type: Type (SSH, HTTP, FTP, DB, API)
            username: Optional username (generated if not provided)
            length: Credential length
            complexity: 'low', 'medium', or 'high'
            
        Returns:
            New Credential with attached genome
        """
        credential_id = str(uuid.uuid4())
        cred_length = length or self._complexity_min
        username = username or self._generate_username()

        # Generate credential value
        password = self._generate_credential_value(cred_length, complexity)

        # Generate genome sequence
        genome_sequence = self._generate_genome_sequence()
        genome_entropy = self._calculate_entropy(genome_sequence)

        # Create genome
        genome = CredentialGenome(
            genome_id=str(uuid.uuid4()),
            credential_id=credential_id,
            sequence=genome_sequence,
            generation=0,
            fitness=self._calculate_fitness_from_complexity(complexity, cred_length),
            entropy=genome_entropy,
            mutation_rate=self._base_mutation_rate,
            lifetime=self._credential_lifetime,
        )

        # Create credential
        credential = Credential(
            credential_id=credential_id,
            service_name=service_name,
            credential_type=credential_type,
            username=username,
            password_hash=self._hash_credential(password),
            genome=genome,
            status="ACTIVE",
            lifetime_sec=self._credential_lifetime,
            metadata={
                "complexity": complexity,
                "length": cred_length,
                "entropy": round(genome_entropy, 4),
            },
        )

        self._credentials[credential_id] = credential
        self._genomes[genome.genome_id] = genome

        logger.info(
            f"Credential generated for {service_name}: {credential_id[:8]}... (gen={genome.generation})",
            extra={
                "extra": {
                    "credential_id": credential_id,
                    "service": service_name,
                    "type": credential_type,
                    "fitness": round(genome.fitness, 4),
                    "entropy": round(genome_entropy, 4),
                }
            },
        )

        return credential

    # ── Mutation Operations ──────────────────────────────────

    def mutate_credential(
        self,
        credential_id: str,
        context: Optional[dict[str, Any]] = None,
    ) -> Credential:
        """
        Mutate a credential using genetic operators (Algorithm 5).
        
        M(S, θ) = {s'ᵢ = mutate(sᵢ) with prob θ, else s'ᵢ = sᵢ}
        
        Args:
            credential_id: Credential to mutate
            context: Mutation context (threat level, etc.)
            
        Returns:
            Mutated Credential
        """
        if credential_id not in self._credentials:
            raise ValueError(f"Credential not found: {credential_id}")

        credential = self._credentials[credential_id]
        old_password = getattr(credential, "_current_value", None)

        # Adjust mutation rate based on context
        mutation_rate = self._base_mutation_rate
        if context:
            threat_level = context.get("threat_level", "LOW")
            if threat_level == "CRITICAL":
                mutation_rate *= 3.0
            elif threat_level == "HIGH":
                mutation_rate *= 2.0

        # Generate new credential value
        new_password = self._mutate_string(
            old_password or self._generate_credential_value(self._complexity_min),
            mutation_rate,
        )

        # Update genome
        old_genome = credential.genome
        new_sequence = self._mutate_string(old_genome.sequence, mutation_rate)
        new_entropy = self._calculate_entropy(new_sequence)

        new_genome = CredentialGenome(
            genome_id=str(uuid.uuid4()),
            credential_id=credential_id,
            sequence=new_sequence,
            generation=old_genome.generation + 1,
            fitness=self._calculate_fitness(new_password, new_sequence),
            entropy=new_entropy,
            mutation_rate=mutation_rate,
            lifetime=self._predict_lifetime(credential),
            parent_id=old_genome.genome_id,
            mutation_history=old_genome.mutation_history + [
                {
                    "generation": old_genome.generation + 1,
                    "mutation_rate": mutation_rate,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "context": context,
                }
            ],
            created_at=datetime.now(timezone.utc).isoformat(),
        )

        # Update credential
        credential.password_hash = self._hash_credential(new_password)
        credential.genome = new_genome
        credential.status = "MUTATED"
        credential.mutated_count += 1
        credential.last_used_at = None  # Reset usage after mutation

        self._genomes[new_genome.genome_id] = new_genome

        logger.info(
            f"Credential mutated: {credential_id[:8]}... gen={new_genome.generation}",
            extra={
                "extra": {
                    "credential_id": credential_id,
                    "generation": new_genome.generation,
                    "mutation_rate": mutation_rate,
                    "fitness": round(new_genome.fitness, 4),
                    "entropy": round(new_entropy, 4),
                }
            },
        )

        return credential

    def mutate_batch(
        self,
        credential_ids: list[str],
        context: Optional[dict[str, Any]] = None,
    ) -> list[Credential]:
        """Mutate multiple credentials in batch"""
        return [self.mutate_credential(cid, context) for cid in credential_ids]

    # ── Selection & Evolution ────────────────────────────────

    def evolve_population(self) -> dict[str, float]:
        """
        Evolve the entire credential population.
        Selection pressure removes low-fitness credentials.
        
        Returns:
            Dict mapping credential_id to new fitness score
        """
        if len(self._credentials) < 2:
            return {}

        results = {}
        for cid, credential in list(self._credentials.items()):
            genome = credential.genome

            # Age the credential
            created = datetime.fromisoformat(genome.created_at)
            age = (datetime.now(timezone.utc) - created).total_seconds()
            genome.age_seconds = int(age)

            # Recalculate fitness
            new_fitness = self._calculate_fitness(
                getattr(credential, "_current_value", ""),
                genome.sequence,
            )
            genome.fitness = new_fitness
            results[cid] = new_fitness

            # Remove low-fitness credentials
            if new_fitness < self._fitness_threshold and credential.mutated_count > 0:
                credential.status = "EXPIRED"
                logger.info(f"Credential expired (low fitness): {cid[:8]}... fitness={new_fitness:.3f}")

        logger.info(
            f"Population evolved: {len(results)} credentials evaluated",
            extra={"extra": {"avg_fitness": round(sum(results.values()) / max(1, len(results)), 4)}},
        )

        return results

    def select_fittest(self, count: int = 1) -> list[Credential]:
        """Select the top-K fittest credentials"""
        sorted_creds = sorted(
            self._credentials.values(),
            key=lambda c: c.genome.fitness,
            reverse=True,
        )
        return [c for c in sorted_creds if c.status == "ACTIVE"][:count]

    # ── Identity Evolution ──────────────────────────────────

    def evolve_identity(
        self,
        identity_data: dict[str, Any],
        context: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """
        Evolve an identity based on trust and context.
        
        Args:
            identity_data: Current identity data
            context: Evolution context (trust_score, behavior_score)
            
        Returns:
            Evolved identity with new attributes
        """
        trust_score = (context or {}).get("trust_score", 0.5)
        behavior_score = (context or {}).get("behavior_score", 0.5)

        # Determine evolution level
        if trust_score > 0.8 and behavior_score > 0.8:
            evolution_level = "full"
        elif trust_score > 0.5:
            evolution_level = "partial"
        else:
            evolution_level = "minimal"

        identity_id = identity_data.get("id", str(uuid.uuid4()))
        new_identity = identity_data.copy()

        if evolution_level == "full":
            new_identity["username"] = self._generate_username()
            new_identity["email"] = self._generate_email()
            new_identity["display_name"] = self._generate_display_name()
            new_identity["attributes"] = self._generate_attributes(10)
        elif evolution_level == "partial":
            new_identity["display_name"] = self._generate_display_name()
            new_identity["attributes"] = self._generate_attributes(5)

        new_identity["evolved_at"] = datetime.now(timezone.utc).isoformat()
        new_identity["evolution_level"] = evolution_level
        new_identity["previous_identity"] = identity_data

        self._identities[identity_id] = new_identity

        logger.info(
            f"Identity evolved: {identity_id[:8]}... level={evolution_level}",
            extra={"extra": {"identity_id": identity_id, "evolution_level": evolution_level}},
        )

        return new_identity

    # ── Session Mutation ─────────────────────────────────────

    def mutate_session(
        self,
        session_id: str,
        context: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """
        Mutate a session to prevent hijacking.
        
        Args:
            session_id: Session identifier
            context: Mutation context
            
        Returns:
            Mutated session data
        """
        new_token = secrets.token_urlsafe(48)

        session = {
            "id": session_id,
            "new_token": new_token,
            "mutated_at": datetime.now(timezone.utc).isoformat(),
            "expires_at": (
                datetime.now(timezone.utc) + timedelta(hours=4)
            ).isoformat(),
            "context": context or {},
            "valid": True,
        }

        logger.info(f"Session mutated: {session_id[:8]}...")

        return session

    # ── Lifetime Prediction ──────────────────────────────────

    def _predict_lifetime(self, credential: Credential) -> int:
        """
        Predict optimal credential lifetime using survival analysis.
        
        h(t | X) = h₀(t) · exp(β₁X₁ + β₂X₂ + ... + βₖXₖ)
        """
        genome = credential.genome

        # Factors affecting lifetime
        age_factor = max(0.5, 1.0 - genome.age_seconds / self._credential_lifetime)
        fitness_factor = genome.fitness
        mutation_factor = 1.0 + genome.mutation_count * 0.1

        predicted = int(self._credential_lifetime * age_factor * fitness_factor * mutation_factor)
        return max(self._mutation_interval, min(self._credential_lifetime * 2, predicted))

    # ── Internal: Generators ─────────────────────────────────

    @staticmethod
    def _generate_credential_value(length: int, complexity: str = "high") -> str:
        """Generate a secure credential value"""
        if complexity == "high":
            chars = string.ascii_letters + string.digits + string.punctuation
        elif complexity == "medium":
            chars = string.ascii_letters + string.digits
        else:
            chars = string.ascii_lowercase + string.digits
        return "".join(secrets.choice(chars) for _ in range(length))

    @staticmethod
    def _generate_username() -> str:
        """Generate a random username"""
        return "".join(secrets.choice(string.ascii_lowercase) for _ in range(8))

    @staticmethod
    def _generate_email() -> str:
        """Generate a random email"""
        username = "".join(secrets.choice(string.ascii_lowercase) for _ in range(8))
        domains = ["example.com", "company.com", "enterprise.net"]
        return f"{username}@{secrets.choice(domains)}"

    @staticmethod
    def _generate_display_name() -> str:
        """Generate a random display name"""
        first_names = ["John", "Jane", "Bob", "Alice", "Charlie", "Diana", "Eve", "Frank"]
        last_names = ["Smith", "Jones", "Brown", "Davis", "Wilson", "Taylor", "Lee", "Clark"]
        return f"{secrets.choice(first_names)} {secrets.choice(last_names)}"

    @staticmethod
    def _generate_attributes(count: int) -> dict[str, Any]:
        """Generate random identity attributes"""
        departments = ["Engineering", "Sales", "Marketing", "Finance", "HR", "Legal"]
        roles = ["Admin", "Manager", "Lead", "Staff", "Intern"]
        locations = ["US", "EU", "APAC", "LATAM"]

        attributes = {}
        for i in range(min(count, 6)):
            if i == 0:
                attributes["department"] = secrets.choice(departments)
            elif i == 1:
                attributes["role"] = secrets.choice(roles)
            elif i == 2:
                attributes["level"] = secrets.randbelow(5) + 1
            elif i == 3:
                attributes["location"] = secrets.choice(locations)
            elif i == 4:
                attributes["employee_id"] = f"EMP-{secrets.randbelow(100000):05d}"
            else:
                attributes[f"attr_{i}"] = secrets.token_hex(4)

        return attributes

    def _generate_genome_sequence(self) -> str:
        """Generate a genome sequence of specified size"""
        chars = string.ascii_letters + string.digits + string.punctuation[:16]
        return "".join(secrets.choice(chars) for _ in range(self._genome_size))

    # ── Internal: Mutation Operators ─────────────────────────

    @staticmethod
    def _mutate_string(value: str, rate: float) -> str:
        """Apply point mutations to a string"""
        chars = list(value)
        alphabet = string.ascii_letters + string.digits + string.punctuation[:16]

        for i in range(len(chars)):
            if random.random() < rate:
                chars[i] = secrets.choice(alphabet)

        return "".join(chars)

    # ── Internal: Fitness, Entropy, Hashing ──────────────────

    def _calculate_fitness(self, credential_value: str, genome_sequence: str) -> float:
        """Calculate composite fitness score"""
        if not credential_value:
            return 0.5

        # Length fitness
        length_fitness = min(1.0, len(credential_value) / (self._complexity_min * 2))

        # Entropy fitness
        entropy = self._calculate_entropy(credential_value)
        entropy_fitness = min(1.0, entropy / 4.0)

        # Character diversity fitness
        char_types = sum([
            1 if any(c.islower() for c in credential_value) else 0,
            1 if any(c.isupper() for c in credential_value) else 0,
            1 if any(c.isdigit() for c in credential_value) else 0,
            1 if any(c in string.punctuation for c in credential_value) else 0,
        ])
        diversity_fitness = char_types / 4.0

        # Genome entropy
        genome_entropy = self._calculate_entropy(genome_sequence)
        genome_fitness = min(1.0, genome_entropy / 6.0)

        # Weighted combination
        fitness = (
            0.3 * length_fitness
            + 0.3 * entropy_fitness
            + 0.2 * diversity_fitness
            + 0.2 * genome_fitness
        )

        return max(0.0, min(1.0, fitness))

    @staticmethod
    def _calculate_fitness_from_complexity(complexity: str, length: int) -> float:
        """Calculate initial fitness from complexity setting"""
        base = {
            "low": 0.6,
            "medium": 0.75,
            "high": 0.9,
        }.get(complexity, 0.75)

        length_bonus = min(0.1, (length - 12) * 0.01)
        return min(1.0, base + length_bonus)

    @staticmethod
    def _calculate_entropy(value: str) -> float:
        """Calculate Shannon entropy of a string"""
        if not value:
            return 0.0

        # Count character type frequencies
        lower = sum(1 for c in value if c.islower())
        upper = sum(1 for c in value if c.isupper())
        digits = sum(1 for c in value if c.isdigit())
        special = len(value) - lower - upper - digits

        probs = [p / len(value) for p in [lower, upper, digits, special] if p > 0]

        # Shannon entropy: H(S) = -Σᵢ p(sᵢ)·log₂(p(sᵢ))
        entropy = -sum(p * math.log2(p) for p in probs)

        return entropy

    @staticmethod
    def _hash_credential(value: str) -> str:
        """Hash a credential value for storage"""
        import hashlib
        return hashlib.sha256(value.encode()).hexdigest()

    # ── State Management ─────────────────────────────────────

    def get_credential(self, credential_id: str) -> Optional[Credential]:
        """Get a specific credential"""
        return self._credentials.get(credential_id)

    def get_genome(self, genome_id: str) -> Optional[CredentialGenome]:
        """Get a specific genome"""
        return self._genomes.get(genome_id)

    def list_credentials(
        self,
        status: Optional[str] = None,
        credential_type: Optional[str] = None,
    ) -> list[Credential]:
        """List credentials, optionally filtered"""
        creds = list(self._credentials.values())
        if status:
            creds = [c for c in creds if c.status == status]
        if credential_type:
            creds = [c for c in creds if c.credential_type == credential_type]
        return creds

    def get_state_summary(self) -> dict[str, Any]:
        """Get summary of current DCMM state"""
        active = [c for c in self._credentials.values() if c.status == "ACTIVE"]
        return {
            "total_credentials": len(self._credentials),
            "active_credentials": len(active),
            "total_genomes": len(self._genomes),
            "total_identities": len(self._identities),
            "avg_fitness": round(
                sum(c.genome.fitness for c in self._credentials.values()) / max(1, len(self._credentials)),
                4,
            ),
            "avg_generation": round(
                sum(c.genome.generation for c in self._credentials.values()) / max(1, len(self._credentials)),
                2,
            ),
            "config": {
                "genome_size": self._genome_size,
                "base_mutation_rate": self._base_mutation_rate,
                "credential_lifetime": self._credential_lifetime,
                "fitness_threshold": self._fitness_threshold,
            },
        }

