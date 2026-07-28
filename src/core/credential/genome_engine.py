"""
Credential Genome Engine - DCMM Implementation
BLACK VEIL Research Contribution: Dynamic Credential Mutation Model (DCMM)

Treats credentials as living organisms with:
- Genome encoding (structure, entropy, stealth)
- Mutation operators (point, insertion, deletion, crossover)
- Evolution through natural selection
- Lifespan management with birth/death lifecycle
"""
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timezone, timedelta
import hashlib
import json
import random
import string
import math
import uuid
import logging

logger = logging.getLogger(__name__)


class CredentialGenome:
    """A credential encoded as a genome with lifecycle management"""
    def __init__(self, credential_type: str = 'password'):
        self.genome_id = str(uuid.uuid4())[:8]
        self.credential_type = credential_type
        self.sequence: str = ''
        self.entropy: float = 0.0
        self.fitness: float = 0.0
        self.stealth_score: float = 1.0
        self.age: float = 0.0
        self.lifespan: float = 86400.0  # 24 hours default
        self.mutation_count: int = 0
        self.created_at = datetime.now(timezone.utc).isoformat()
        self.last_mutated = self.created_at
        self.metadata: Dict[str, Any] = {}


class CredentialGenomeEngine:
    """
    Credential Genome Engine (DCMM).

    Manages credentials as living genomes with:
    - Evolution through genetic operators
    - Entropy optimization for strength
    - Stealth scoring to avoid detection
    - Lifespan-based automatic rotation
    - Population diversity maintenance
    """

    def __init__(self):
        self._population: Dict[str, CredentialGenome] = {}
        self._population_size = 50
        self._mutation_rate = 0.01
        self._min_entropy = 3.5
        logger.info("CredentialGenomeEngine initialized")

    def generate_credential(self, credential_type: str = 'password') -> Dict[str, Any]:
        """Generate a new credential genome"""
        genome = CredentialGenome(credential_type)
        genome.sequence = self._generate_sequence()
        genome.entropy = self._calculate_entropy(genome.sequence)
        genome.fitness = self._calculate_fitness(genome)
        genome.lifespan = self._calculate_lifespan(genome)
        genome.metadata = {
            'character_sets': self._detect_character_sets(genome.sequence),
            'length': len(genome.sequence),
            'generation': 1,
        }

        self._population[genome.genome_id] = genome
        logger.info(f"Credential generated: {genome.genome_id[:8]} entropy={genome.entropy:.2f}")
        return self._genome_to_dict(genome)

    def mutate_credential(self, genome_id: str) -> Optional[Dict[str, Any]]:
        """Apply mutation operator to a credential genome"""
        if genome_id not in self._population:
            return None

        genome = self._population[genome_id]
        genome.sequence = self._apply_mutation(genome.sequence)
        genome.entropy = self._calculate_entropy(genome.sequence)
        genome.fitness = self._calculate_fitness(genome)
        genome.mutation_count += 1
        genome.last_mutated = datetime.now(timezone.utc).isoformat()
        genome.metadata['generation'] = genome.metadata.get('generation', 1) + 1

        logger.info(f"Credential mutated: {genome_id[:8]} generation={genome.metadata['generation']}")
        return self._genome_to_dict(genome)

    def evaluate_fitness(self, genome_id: str) -> Optional[float]:
        """Evaluate fitness of a credential genome"""
        genome = self._population.get(genome_id)
        if not genome:
            return None
        genome.fitness = self._calculate_fitness(genome)
        return genome.fitness

    def select_fittest(self, top_k: int = 5) -> List[Dict[str, Any]]:
        """Select the fittest credentials from the population"""
        sorted_genomes = sorted(
            self._population.values(),
            key=lambda g: g.fitness,
            reverse=True,
        )
        return [self._genome_to_dict(g) for g in sorted_genomes[:top_k]]

    def cull_population(self) -> int:
        """Remove expired and low-fitness credentials"""
        now = datetime.now(timezone.utc)
        to_remove = []

        for gid, genome in self._population.items():
            created = datetime.fromisoformat(genome.created_at)
            age = (now - created).total_seconds()
            genome.age = age

            if age > genome.lifespan or genome.fitness < 0.3:
                to_remove.append(gid)

        for gid in to_remove:
            del self._population[gid]

        logger.info(f"Culled {len(to_remove)} credentials (population: {len(self._population)})")
        return len(to_remove)

    def _generate_sequence(self, length: int = 32) -> str:
        """Generate a random credential sequence"""
        chars = string.ascii_letters + string.digits + "!@#$%^&*()_+-=[]{}|;:,.<>?"
        return ''.join(random.choice(chars) for _ in range(length))

    def _apply_mutation(self, sequence: str) -> str:
        """Apply genetic mutation to sequence"""
        seq = list(sequence)
        mutation_types = ['point', 'insert', 'delete', 'swap']

        for i in range(len(seq)):
            if random.random() < self._mutation_rate:
                mutation = random.choice(mutation_types)
                if mutation == 'point':
                    seq[i] = random.choice(string.ascii_letters + string.digits)
                elif mutation == 'swap' and i < len(seq) - 1:
                    seq[i], seq[i + 1] = seq[i + 1], seq[i]

        if random.random() < self._mutation_rate * 2:
            # Insert random character
            pos = random.randint(0, len(seq))
            seq.insert(pos, random.choice(string.ascii_letters + string.digits))

        if random.random() < self._mutation_rate and len(seq) > 8:
            # Delete random character
            pos = random.randint(0, len(seq) - 1)
            seq.pop(pos)

        return ''.join(seq)

    def _calculate_entropy(self, sequence: str) -> float:
        """Calculate Shannon entropy of credential"""
        if not sequence:
            return 0.0
        freq = {}
        for c in sequence:
            freq[c] = freq.get(c, 0) + 1
        entropy = 0.0
        for count in freq.values():
            p = count / len(sequence)
            entropy -= p * math.log2(p)
        return entropy

    def _calculate_fitness(self, genome: CredentialGenome) -> float:
        """Calculate fitness score for a credential genome"""
        entropy_score = min(1.0, genome.entropy / 5.0)
        length_score = min(1.0, len(genome.sequence) / 32.0)
        diversity_score = len(self._detect_character_sets(genome.sequence)) / 4.0

        fitness = entropy_score * 0.4 + length_score * 0.3 + diversity_score * 0.3
        return min(1.0, max(0.0, fitness))

    def _calculate_lifespan(self, genome: CredentialGenome) -> float:
        """Calculate lifespan based on credential strength"""
        base = 86400.0  # 24 hours
        strength_bonus = genome.fitness * 86400.0  # Up to 24h bonus
        return base + strength_bonus

    @staticmethod
    def _detect_character_sets(sequence: str) -> List[str]:
        """Detect which character sets are used"""
        sets = []
        if any(c.islower() for c in sequence):
            sets.append('lowercase')
        if any(c.isupper() for c in sequence):
            sets.append('uppercase')
        if any(c.isdigit() for c in sequence):
            sets.append('digits')
        if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in sequence):
            sets.append('special')
        return sets

    @staticmethod
    def _genome_to_dict(genome: CredentialGenome) -> Dict[str, Any]:
        """Convert genome to dictionary"""
        return {
            'genome_id': genome.genome_id,
            'credential_type': genome.credential_type,
            'entropy': round(genome.entropy, 4),
            'fitness': round(genome.fitness, 4),
            'stealth_score': round(genome.stealth_score, 4),
            'age': round(genome.age, 1),
            'lifespan': round(genome.lifespan, 1),
            'mutation_count': genome.mutation_count,
            'character_sets': genome.metadata.get('character_sets', []),
            'length': genome.metadata.get('length', 0),
            'generation': genome.metadata.get('generation', 1),
        }

    def get_state_summary(self) -> Dict[str, Any]:
        """Get summary of credential genome engine state"""
        pop = self._population.values()
        return {
            'population_size': len(pop),
            'avg_entropy': round(sum(g.entropy for g in pop) / max(1, len(pop)), 4) if pop else 0,
            'avg_fitness': round(sum(g.fitness for g in pop) / max(1, len(pop)), 4) if pop else 0,
            'avg_age': round(sum(g.age for g in pop) / max(1, len(pop)), 1) if pop else 0,
            'total_mutations': sum(g.mutation_count for g in pop),
        }

