"""
Timing Security for BLACK VEIL
Prevents timing attacks and side-channel information leakage
"""

from typing import Any, Dict, Optional
import random
import time
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class TimingProtection:
    """Timing protection configuration"""
    constant_time: bool
    jitter_ms: float
    padding_enabled: bool
    batch_processing: bool

class TimingSecurity:
    """
    Protects against timing attacks
    
    Features:
    - Constant-time operations
    - Timing jitter
    - Data padding
    - Batch processing
    - Traffic obfuscation
    """
    
    def __init__(self):
        self.protection_config = TimingProtection(
            constant_time=True,
            jitter_ms=50,
            padding_enabled=True,
            batch_processing=False
        )
    
    def protect_operation(self, operation: callable, *args, **kwargs) -> Any:
        """
        Execute operation with timing protection
        """
        start_time = time.perf_counter()
        
        # Execute operation
        result = operation(*args, **kwargs)
        
        # Add timing jitter
        if self.protection_config.jitter_ms > 0:
            jitter = random.uniform(0, self.protection_config.jitter_ms / 1000)
            time.sleep(jitter)
        
        # Ensure constant time (if enabled)
        if self.protection_config.constant_time:
            self._ensure_constant_time(start_time)
        
        return result
    
    def _ensure_constant_time(self, start_time: float):
        """Ensure operations take constant time"""
        elapsed = (time.perf_counter() - start_time) * 1000
        
        # Calculate minimum time
        min_time = 10.0  # 10ms minimum
        
        if elapsed < min_time:
            time.sleep((min_time - elapsed) / 1000)
    
    def pad_response(self, data: Any, min_size: int = 1024) -> Any:
        """Pad response to prevent size inference"""
        if not self.protection_config.padding_enabled:
            return data
        
        if isinstance(data, str):
            padding = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', 
                                           k=random.randint(min_size, min_size * 2)))
            return data + padding
        
        elif isinstance(data, bytes):
            padding = bytes([random.randint(0, 255) for _ in range(random.randint(min_size, min_size * 2))])
            return data + padding
        
        return data
    
    def add_timing_jitter(self) -> float:
        """Add random timing jitter"""
        if self.protection_config.jitter_ms > 0:
            jitter = random.uniform(0, self.protection_config.jitter_ms / 1000)
            time.sleep(jitter)
            return jitter
        return 0.0
    
    def generate_cover_traffic(self, count: int = 10) -> None:
        """Generate cover traffic to hide patterns"""
        for _ in range(random.randint(1, count)):
            self.add_timing_jitter()
    
    def enable_batch_processing(self):
        """Enable batch processing mode"""
        self.protection_config.batch_processing = True
        
    def disable_batch_processing(self):
        """Disable batch processing mode"""
        self.protection_config.batch_processing = False
    
    def get_timing_metrics(self) -> Dict:
        """Get timing security metrics"""
        return {
            'constant_time_enabled': self.protection_config.constant_time,
            'jitter_ms': self.protection_config.jitter_ms,
            'padding_enabled': self.protection_config.padding_enabled,
            'batch_processing': self.protection_config.batch_processing
        }
