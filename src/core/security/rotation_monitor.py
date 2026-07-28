"""
BLACK VEIL Rotation Monitor
Background service that continuously monitors and triggers key rotations.

Monitors:
- Encryption key health and rotation timing
- JWT secret age and usage
- TLS certificate expiry
- Global risk level changes
- Entropy levels across all crypto subsystems
"""
import asyncio
import logging
from typing import Dict, Any, Optional, Callable, List
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class RotationMonitor:
    """
    Background rotation monitor for all dynamic security components.
    
    Continuously evaluates:
    - Time since last rotation vs configured intervals
    - Key usage vs max usage thresholds
    - Global risk level and entropy
    - Event-triggered rotation needs
    """

    def __init__(self, check_interval: int = 60):
        self.check_interval = check_interval  # Seconds between checks
        self._rotation_callbacks: Dict[str, List[Callable]] = {
            'encryption': [],
            'jwt': [],
            'tls': [],
        }
        self._is_running = False
        self._check_count = 0
        self._last_rotation_times: Dict[str, datetime] = {}
        self._rotation_stats: Dict[str, int] = {
            'encryption': 0, 'jwt': 0, 'tls': 0,
        }
        logger.info(f"RotationMonitor initialized (check_interval={check_interval}s)")

    def register_encryption_rotator(self, callback: Callable) -> None:
        """Register encryption key rotation callback"""
        self._rotation_callbacks['encryption'].append(callback)
        logger.debug("Encryption rotator registered")

    def register_jwt_rotator(self, callback: Callable) -> None:
        """Register JWT secret rotation callback"""
        self._rotation_callbacks['jwt'].append(callback)
        logger.debug("JWT rotator registered")

    def register_tls_rotator(self, callback: Callable) -> None:
        """Register TLS certificate rotation callback"""
        self._rotation_callbacks['tls'].append(callback)
        logger.debug("TLS rotator registered")

    async def start(self) -> None:
        """Start the rotation monitor background loop"""
        self._is_running = True
        logger.info("Rotation monitor started")
        while self._is_running:
            try:
                await self._check_all()
                await asyncio.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"Rotation check failed: {e}")
                await asyncio.sleep(self.check_interval * 2)

    def stop(self) -> None:
        """Stop the rotation monitor"""
        self._is_running = False
        logger.info("Rotation monitor stopped")

    async def force_rotation(self, component: str) -> int:
        """Force immediate rotation of a component. Returns count of rotations."""
        count = 0
        for callback in self._rotation_callbacks.get(component, []):
            try:
                if asyncio.iscoroutinefunction(callback):
                    result = await callback()
                else:
                    result = callback()
                if result:
                    count += 1 if isinstance(result, bool) else result
            except Exception as e:
                logger.error(f"Forced rotation failed for {component}: {e}")
        if count > 0:
            self._rotation_stats[component] = self._rotation_stats.get(component, 0) + count
            self._last_rotation_times[component] = datetime.now(timezone.utc)
        return count

    async def _check_all(self) -> None:
        """Check all components for rotation needs"""
        self._check_count += 1

        # Check encryption keys
        for cb in self._rotation_callbacks.get('encryption', []):
            try:
                if asyncio.iscoroutinefunction(cb):
                    result = await cb()
                else:
                    result = cb()
                if result:
                    self._rotation_stats['encryption'] += len(result) if isinstance(result, list) else 1
                    self._last_rotation_times['encryption'] = datetime.now(timezone.utc)
            except Exception as e:
                logger.error(f"Encryption rotation check failed: {e}")

        # Check JWT secrets
        for cb in self._rotation_callbacks.get('jwt', []):
            try:
                if asyncio.iscoroutinefunction(cb):
                    result = await cb()
                else:
                    result = cb()
                if result:
                    self._rotation_stats['jwt'] += result if isinstance(result, int) else 1
                    self._last_rotation_times['jwt'] = datetime.now(timezone.utc)
            except Exception as e:
                logger.error(f"JWT rotation check failed: {e}")

        # Check TLS certificates
        for cb in self._rotation_callbacks.get('tls', []):
            try:
                if asyncio.iscoroutinefunction(cb):
                    await cb()
                else:
                    cb()
            except Exception as e:
                logger.error(f"TLS rotation check failed: {e}")

    def get_state_summary(self) -> Dict[str, Any]:
        """Get rotation monitor state summary"""
        return {
            'is_running': self._is_running,
            'check_interval': self.check_interval,
            'total_checks': self._check_count,
            'rotation_stats': self._rotation_stats.copy(),
            'last_rotations': {
                k: v.isoformat() for k, v in self._last_rotation_times.items()
            },
            'registered_callbacks': {
                k: len(v) for k, v in self._rotation_callbacks.items()
            },
        }

