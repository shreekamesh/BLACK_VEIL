"""
Enhanced Event Bus with Priority, Retry, Dead-Letter Queue.

Provides:
- Priority queuing (CRITICAL > HIGH > MEDIUM > LOW > DEBUG)
- Retry handling with exponential backoff
- Dead-letter queue for failed events
- Correlation IDs for distributed tracing
- Performance metrics
"""
from typing import Dict, Any, Callable, List, Optional
from datetime import datetime, timezone
import asyncio
import logging
from collections import defaultdict
from enum import Enum
import heapq
import uuid

logger = logging.getLogger(__name__)


class EventPriority(Enum):
    """Event priorities — lower number = higher priority"""
    CRITICAL = 0
    HIGH = 1
    MEDIUM = 2
    LOW = 3
    DEBUG = 4


class EventBus:
    """
    Enhanced Event Bus for BLACK VEIL.

    Features:
    - Priority queuing (CRITICAL events processed first)
    - Retry handling with exponential backoff
    - Dead-letter queue for persistently failing events
    - Correlation IDs for distributed tracing
    - Performance metrics
    """

    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = defaultdict(list)
        self.priority_queues: Dict[int, List] = defaultdict(list)
        self.event_history: List[Dict[str, Any]] = []
        self.dead_letter_queue: List[Dict[str, Any]] = []
        self.max_history = 10000
        self.max_retries = 3
        self.is_running = False

        # Correlation tracking
        self.correlation_map: Dict[str, List[str]] = defaultdict(list)

        # Metrics
        self.metrics = {
            'total_published': 0,
            'total_processed': 0,
            'total_retries': 0,
            'total_failures': 0,
            'avg_latency': 0.0,
        }

    def subscribe(self, event_type: str, callback: Callable) -> None:
        """Subscribe to an event type"""
        self.subscribers[event_type].append(callback)
        logger.info(f"Subscribed to {event_type}")

    def unsubscribe(self, event_type: str, callback: Callable) -> None:
        """Unsubscribe from an event type"""
        if event_type in self.subscribers:
            self.subscribers[event_type] = [
                cb for cb in self.subscribers[event_type]
                if cb != callback
            ]

    async def publish(self, event_type: str, data: Dict[str, Any],
                      priority: EventPriority = EventPriority.MEDIUM,
                      correlation_id: Optional[str] = None) -> List[Any]:
        """
        Publish an event with priority and correlation.

        Args:
            event_type: Type of event (e.g., 'event_processed', 'anomaly_detected')
            data: Event payload
            priority: Priority level (default MEDIUM)
            correlation_id: Optional correlation ID for tracing

        Returns:
            List of results from subscribers
        """
        # Create event with metadata
        event = {
            'type': event_type,
            'data': data,
            'priority': priority.value,
            'correlation_id': correlation_id or str(uuid.uuid4()),
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'retry_count': 0,
        }

        # Store for auditing
        self.event_history.append(event)
        if len(self.event_history) > self.max_history:
            self.event_history.pop(0)

        # Track correlation
        if correlation_id:
            self.correlation_map[correlation_id].append(event['correlation_id'])

        # Push to priority queue
        heapq.heappush(self.priority_queues[priority.value], event)

        self.metrics['total_published'] += 1

        # Process immediately if running
        if self.is_running:
            return await self._process_event(event)

        return []

    async def _process_event(self, event: Dict[str, Any]) -> List[Any]:
        """Process a single event with retries"""
        event_type = event['type']
        results = []

        if event_type not in self.subscribers:
            return results

        start_time = datetime.now(timezone.utc)

        for callback in self.subscribers.get(event_type, []):
            try:
                if asyncio.iscoroutinefunction(callback):
                    result = await callback(event)
                else:
                    result = callback(event)
                results.append(result)
                self.metrics['total_processed'] += 1

            except Exception as e:
                logger.error(f"Event handler error: {e}")

                # Retry logic with exponential backoff
                if event['retry_count'] < self.max_retries:
                    event['retry_count'] += 1
                    self.metrics['total_retries'] += 1

                    backoff = 2 ** event['retry_count']  # Exponential backoff
                    await asyncio.sleep(backoff)

                    # Re-publish
                    await self.publish(
                        event_type,
                        event['data'],
                        EventPriority(event['priority']),
                        event['correlation_id'],
                    )
                else:
                    # Send to dead-letter queue
                    self.dead_letter_queue.append({
                        'event': event,
                        'error': str(e),
                        'timestamp': datetime.now(timezone.utc).isoformat(),
                    })
                    self.metrics['total_failures'] += 1
                    logger.error(f"Event moved to DLQ: {event_type}")

                results.append({'error': str(e)})

        # Record latency
        latency = (datetime.now(timezone.utc) - start_time).total_seconds()
        total = self.metrics['total_processed']
        self.metrics['avg_latency'] = (
            (self.metrics['avg_latency'] * (total - 1) + latency) / total
            if total > 0 else latency
        )

        return results

    async def start_event_loop(self) -> None:
        """Start the event loop with priority processing"""
        self.is_running = True
        logger.info("Event Bus started with priority queuing")

        while self.is_running:
            processed = False

            # Process events by priority order
            for priority in [EventPriority.CRITICAL, EventPriority.HIGH,
                             EventPriority.MEDIUM, EventPriority.LOW,
                             EventPriority.DEBUG]:
                queue = self.priority_queues[priority.value]
                if queue:
                    event = heapq.heappop(queue)
                    await self._process_event(event)
                    processed = True
                    break

            if not processed:
                await asyncio.sleep(0.01)

    def get_correlation_trace(self, correlation_id: str) -> List[Dict[str, Any]]:
        """Get all events in a correlation trace"""
        return [
            event for event in self.event_history
            if event['correlation_id'] == correlation_id
        ]

    def get_dead_letter_queue(self) -> List[Dict[str, Any]]:
        """Get dead-letter queue contents"""
        return self.dead_letter_queue

    def retry_dead_letter(self) -> None:
        """Retry all events in the dead-letter queue"""
        for item in self.dead_letter_queue:
            event = item['event']
            event['retry_count'] = 0

            # Re-publish
            self.publish(
                event['type'],
                event['data'],
                EventPriority(event['priority']),
                event['correlation_id'],
            )

        self.dead_letter_queue = []

    def get_metrics(self) -> Dict[str, Any]:
        """Get event bus metrics"""
        return {
            **self.metrics,
            'queue_sizes': {
                'critical': len(self.priority_queues[0]),
                'high': len(self.priority_queues[1]),
                'medium': len(self.priority_queues[2]),
                'low': len(self.priority_queues[3]),
                'debug': len(self.priority_queues[4]),
            },
            'dead_letter_size': len(self.dead_letter_queue),
            'total_events_stored': len(self.event_history),
        }

    def stop(self) -> None:
        """Stop the event loop"""
        self.is_running = False
        logger.info("Event Bus stopped")
