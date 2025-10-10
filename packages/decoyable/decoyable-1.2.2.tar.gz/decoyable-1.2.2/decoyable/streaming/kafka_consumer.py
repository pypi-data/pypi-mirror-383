"""
decoyable/streaming/kafka_consumer.py

Kafka consumer groups for processing attack events asynchronously.
Handles AI analysis, alert forwarding, and data persistence.
"""

import asyncio
import json
import logging
from typing import Any, Dict

from decoyable.core.config import settings

logger = logging.getLogger(__name__)

# Import Kafka classes for patching in tests
try:
    from aiokafka import AIOKafkaConsumer

    KAFKA_AVAILABLE = True
except ImportError:
    AIOKafkaConsumer = None  # For patching in tests
    KAFKA_AVAILABLE = False
    logger.warning("aiokafka not available. Kafka streaming disabled.")


class AttackEventConsumer:
    """
    Kafka consumer for processing attack events.

    Consumer group that handles different types of processing:
    - AI/LLM analysis
    - SOC/SIEM alert forwarding
    - Database persistence
    """

    def __init__(self, consumer_type: str):
        self.consumer_type = consumer_type  # 'analysis', 'alerts', 'persistence'
        self.enabled = settings.kafka_enabled
        self.consumer = None
        self.topic = settings.kafka_attack_topic
        self.group_id = f"decoyable-{consumer_type}"

        if self.enabled:
            self._init_consumer()

    def _init_consumer(self) -> None:
        """Initialize Kafka consumer if enabled."""
        if not KAFKA_AVAILABLE:
            logger.warning("aiokafka not installed, Kafka streaming disabled")
            self.enabled = False
            return
            
        try:
            from aiokafka import AIOKafkaConsumer

            self.consumer = AIOKafkaConsumer(
                self.topic,
                bootstrap_servers=settings.kafka_bootstrap_servers,
                group_id=self.group_id,
                value_deserializer=lambda v: self._safe_json_loads(v.decode("utf-8")),
                key_deserializer=lambda k: k.decode("utf-8") if k else None,
                auto_offset_reset="latest",  # Start from latest to avoid backlogs
                enable_auto_commit=True,
                auto_commit_interval_ms=1000,
                max_poll_records=10,  # Process in small batches
            )
            logger.info(f"Kafka consumer initialized for {self.consumer_type}")
        except Exception as e:
            logger.error(f"Failed to initialize Kafka consumer: {e}")
            self.enabled = False

    async def start(self) -> None:
        """Start the Kafka consumer."""
        if self.enabled and self.consumer:
            try:
                await self.consumer.start()
                logger.info(f"Kafka consumer started for {self.consumer_type}")
            except Exception as e:
                logger.error(f"Failed to start Kafka consumer: {e}")
                self.enabled = False

    def _safe_json_loads(self, data: str) -> dict:
        """Safely deserialize JSON data with validation."""
        try:
            # Safe: JSON from Kafka message stream with type validation
            parsed = json.loads(data)
            if not isinstance(parsed, dict):
                logger.warning(f"Invalid Kafka message format: expected dict, got {type(parsed)}")
                return {}
            return parsed
        except (json.JSONDecodeError, TypeError) as e:
            logger.warning(f"Failed to parse Kafka message: {e}")
            return {}

    async def stop(self) -> None:
        """Stop the Kafka consumer."""
        if self.enabled and self.consumer:
            try:
                await self.consumer.stop()
                logger.info(f"Kafka consumer stopped for {self.consumer_type}")
            except Exception as e:
                logger.error(f"Error stopping Kafka consumer: {e}")

    async def consume_events(self) -> None:
        """Main consumption loop."""
        if not self.enabled or not self.consumer:
            logger.warning(f"Consumer {self.consumer_type} not enabled or initialized")
            return

        logger.info(f"Starting event consumption for {self.consumer_type}")

        try:
            async for message in self.consumer:
                try:
                    event = message.value
                    await self._process_event(event)
                except Exception as e:
                    logger.error(f"Error processing event in {self.consumer_type}: {e}")
                    # Continue processing other events
                    continue

        except Exception as e:
            logger.error(f"Consumer {self.consumer_type} failed: {e}")
        finally:
            await self.stop()

    async def _process_event(self, event: Dict[str, Any]) -> None:
        """Process individual events based on consumer type."""
        event_type = event.get("event_type")
        data = event.get("data", {})

        if self.consumer_type == "analysis":
            await self._process_analysis_event(event_type, data)
        elif self.consumer_type == "alerts":
            await self._process_alert_event(event_type, data)
        elif self.consumer_type == "persistence":
            await self._process_persistence_event(event_type, data)
        else:
            logger.warning(f"Unknown consumer type: {self.consumer_type}")

    async def _process_analysis_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Process events for AI/LLM analysis."""
        if event_type == "attack_detected":
            try:
                # Perform AI analysis using stub function
                analysis_result = await analyze_attack_async(data)

                # Apply adaptive defense (non-blocking)
                await apply_adaptive_defense(data)

                logger.debug(f"AI analysis completed for attack from {data.get('ip_address')}")

            except Exception as e:
                logger.error(f"AI analysis failed: {e}")

    async def _process_alert_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Process events for SOC/SIEM alert forwarding."""
        if event_type in ("attack_detected", "security_alert"):
            try:
                # Forward to SOC/SIEM using stub function
                await forward_alert(data)

                logger.debug(f"Alert forwarded for {event_type}")

            except Exception as e:
                logger.error(f"Alert forwarding failed: {e}")

    async def _process_persistence_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Process events for database persistence."""
        try:
            if event_type == "attack_detected":
                # Store attack data in knowledge base using stub
                attack_id = knowledge_base.store_attack(data)
                logger.debug(f"Attack stored with ID: {attack_id}")

            elif event_type == "security_alert":
                # Store alert data (using same method for now)
                alert_id = knowledge_base.store_attack(data)
                logger.debug(f"Alert stored with ID: {alert_id}")

        except Exception as e:
            logger.error(f"Data persistence failed: {e}")


# Consumer instances for different processing types
analysis_consumer = AttackEventConsumer("analysis")
alert_consumer = AttackEventConsumer("alerts")
persistence_consumer = AttackEventConsumer("persistence")


async def start_all_consumers() -> None:
    """Start all Kafka consumers."""
    if not settings.kafka_enabled:
        logger.info("Kafka streaming disabled, skipping consumer startup")
        return

    consumers = [analysis_consumer, alert_consumer, persistence_consumer]

    # Start all consumers concurrently
    await asyncio.gather(*[consumer.start() for consumer in consumers])

    logger.info("All Kafka consumers started")

    # Start consumption tasks
    tasks = []
    for consumer in consumers:
        task = asyncio.create_task(consumer.consume_events())
        tasks.append(task)

    # Wait for all tasks (they run indefinitely)
    await asyncio.gather(*tasks, return_exceptions=True)


async def stop_all_consumers() -> None:
    """Stop all Kafka consumers."""
    consumers = [analysis_consumer, alert_consumer, persistence_consumer]

    await asyncio.gather(*[consumer.stop() for consumer in consumers])

    logger.info("All Kafka consumers stopped")


# Stub functions for testing - to be implemented
async def analyze_attack_async(attack_data: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze attack data asynchronously."""
    logger.info(f"Analyzing attack: {attack_data}")
    return {"attack_type": "unknown", "confidence": 0.5}


async def apply_adaptive_defense(attack_data: Dict[str, Any]) -> None:
    """Apply adaptive defense rules based on attack analysis."""
    logger.info(f"Applying adaptive defense for attack: {attack_data}")


async def forward_alert(alert_data: Dict[str, Any]) -> None:
    """Forward alert to external security systems."""
    logger.info(f"Forwarding alert: {alert_data}")


class MockKnowledgeBase:
    """Mock knowledge base for testing."""
    def store_attack(self, attack_data: Dict[str, Any]) -> int:
        """Store attack data and return ID."""
        logger.info(f"Storing attack: {attack_data}")
        return 123


knowledge_base = MockKnowledgeBase()
