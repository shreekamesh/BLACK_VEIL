"""
Learning Layer - Continuous improvement across all subsystems
BLACK VEIL - Orchestrates model/policy/trust/memory/strategy updates

Core Principle:
Every event is a learning opportunity. The system continuously improves
its models, policies, trust scoring, and strategies over time.
"""
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timezone
import asyncio
import logging

logger = logging.getLogger(__name__)


class LearningEngine:
    """
    Orchestrates continuous learning across:
    - Model updates (retrain with new data)
    - Policy updates (adapt rules based on outcomes)
    - Trust updates (refine trust scoring)
    - Memory updates (evolve knowledge graph)
    - Strategy optimization (reinforcement learning)

    Runs as a background loop, processing batches of events.
    """

    def __init__(self):
        self._learning_interval = 3600  # 1 hour default
        self._batch_size = 100
        self._is_running = False
        self._cycle_count = 0

        # Registered update callbacks
        self._model_updaters: List[Callable] = []
        self._policy_updaters: List[Callable] = []
        self._trust_updaters: List[Callable] = []
        self._memory_updaters: List[Callable] = []
        self._strategy_updaters: List[Callable] = []

        # Learning statistics
        self._learning_history: List[Dict[str, Any]] = []
        self._decisions_processed = 0
        self._events_processed = 0

        logger.info("LearningEngine initialized")

    # ── Registration Methods ──────────────────────────────────

    def register_model_updater(self, updater: Callable) -> None:
        """Register a model update callback"""
        self._model_updaters.append(updater)
        logger.debug(f"Model updater registered: {updater.__name__}")

    def register_policy_updater(self, updater: Callable) -> None:
        """Register a policy update callback"""
        self._policy_updaters.append(updater)
        logger.debug(f"Policy updater registered: {updater.__name__}")

    def register_trust_updater(self, updater: Callable) -> None:
        """Register a trust update callback"""
        self._trust_updaters.append(updater)
        logger.debug(f"Trust updater registered: {updater.__name__}")

    def register_memory_updater(self, updater: Callable) -> None:
        """Register a memory/knowledge update callback"""
        self._memory_updaters.append(updater)
        logger.debug(f"Memory updater registered: {updater.__name__}")

    def register_strategy_updater(self, updater: Callable) -> None:
        """Register a strategy optimization callback"""
        self._strategy_updaters.append(updater)
        logger.debug(f"Strategy updater registered: {updater.__name__}")

    # ── Learning Cycle ────────────────────────────────────────

    async def start_loop(self, interval: int = 3600) -> None:
        """Start the continuous learning loop"""
        self._learning_interval = interval
        self._is_running = True

        logger.info(f"Learning loop started (interval={interval}s)")
        while self._is_running:
            try:
                await self._execute_cycle()
            except Exception as e:
                logger.error(f"Learning cycle failed: {e}")
            await asyncio.sleep(self._learning_interval)

    def stop_loop(self) -> None:
        """Stop the learning loop"""
        self._is_running = False
        logger.info("Learning loop stopped")

    async def execute_cycle(self, decisions: List[Dict] = None,
                            events: List[Dict] = None) -> Dict[str, Any]:
        """Execute one learning cycle (can be called manually)"""
        return await self._execute_cycle(decisions, events)

    async def _execute_cycle(self, decisions: List[Dict] = None,
                             events: List[Dict] = None) -> Dict[str, Any]:
        """Execute one learning cycle internally"""
        self._cycle_count += 1
        cycle_id = f"LRN-{self._cycle_count}"

        logger.info(f"Learning cycle {cycle_id} starting...")
        results = {
            'cycle_id': cycle_id,
            'models_updated': 0,
            'policies_updated': 0,
            'trust_updated': 0,
            'memory_updated': 0,
            'strategies_optimized': 0,
            'timestamp': datetime.now(timezone.utc).isoformat(),
        }

        # 1. Update models
        if decisions:
            for updater in self._model_updaters:
                try:
                    await updater(decisions, events)
                    results['models_updated'] += 1
                except Exception as e:
                    logger.error(f"Model updater {updater.__name__} failed: {e}")

        # 2. Update policies
        if decisions:
            for updater in self._policy_updaters:
                try:
                    await updater(decisions)
                    results['policies_updated'] += 1
                except Exception as e:
                    logger.error(f"Policy updater {updater.__name__} failed: {e}")

        # 3. Update trust
        if events:
            for updater in self._trust_updaters:
                try:
                    await updater(events)
                    results['trust_updated'] += 1
                except Exception as e:
                    logger.error(f"Trust updater {updater.__name__} failed: {e}")

        # 4. Update memory
        if events and decisions:
            for updater in self._memory_updaters:
                try:
                    await updater(events, decisions)
                    results['memory_updated'] += 1
                except Exception as e:
                    logger.error(f"Memory updater {updater.__name__} failed: {e}")

        # 5. Optimize strategies
        if decisions:
            for updater in self._strategy_updaters:
                try:
                    await updater(decisions)
                    results['strategies_optimized'] += 1
                except Exception as e:
                    logger.error(f"Strategy updater {updater.__name__} failed: {e}")

        # Update statistics
        if decisions:
            self._decisions_processed += len(decisions)
        if events:
            self._events_processed += len(events)

        self._learning_history.append(results)

        logger.info(
            f"Learning cycle {cycle_id} completed: "
            f"{results['models_updated']} models, "
            f"{results['policies_updated']} policies, "
            f"{results['trust_updated']} trust, "
            f"{results['memory_updated']} memory, "
            f"{results['strategies_optimized']} strategies"
        )

        return results

    # ── Statistics ────────────────────────────────────────────

    def get_learning_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent learning cycle results"""
        return self._learning_history[-limit:]

    def get_state_summary(self) -> Dict[str, Any]:
        """Get summary of learning engine state"""
        if not self._learning_history:
            return {
                'cycles_completed': 0,
                'decisions_processed': 0,
                'events_processed': 0,
                'is_running': self._is_running,
                'interval': self._learning_interval,
                'registered_updaters': {
                    'models': len(self._model_updaters),
                    'policies': len(self._policy_updaters),
                    'trust': len(self._trust_updaters),
                    'memory': len(self._memory_updaters),
                    'strategies': len(self._strategy_updaters),
                },
            }

        last = self._learning_history[-1]
        return {
            'cycles_completed': self._cycle_count,
            'decisions_processed': self._decisions_processed,
            'events_processed': self._events_processed,
            'is_running': self._is_running,
            'interval': self._learning_interval,
            'last_cycle': last,
            'registered_updaters': {
                'models': len(self._model_updaters),
                'policies': len(self._policy_updaters),
                'trust': len(self._trust_updaters),
                'memory': len(self._memory_updaters),
                'strategies': len(self._strategy_updaters),
            },
        }

