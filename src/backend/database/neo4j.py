"""
BLACK VEIL V5 - Neo4j Graph Database Connection
Async graph database for the Living Attack Memory Graph (LAMG)
"""
import logging
from typing import Optional, List, Dict, Any

from neo4j import AsyncGraphDatabase, AsyncDriver

from src.backend.config import (
    NEO4J_USER,
    NEO4J_PASSWORD,
    NEO4J_HOST,
    NEO4J_PORT,
    NEO4J_DATABASE,
    NEO4J_MAX_CONNECTION_LIFETIME,
    NEO4J_MAX_CONNECTION_POOL_SIZE,
)

logger = logging.getLogger(__name__)


class Neo4jDatabase:
    """Neo4j async graph database connection manager"""

    def __init__(self):
        self._driver: Optional[AsyncDriver] = None

    async def initialize(self) -> None:
        """Initialize Neo4j connection"""
        if self._driver is not None:
            logger.debug("Neo4j already initialized")
            return

        uri = f"neo4j://{NEO4J_HOST}:{NEO4J_PORT}"
        logger.info("Connecting to Neo4j at %s:%s", NEO4J_HOST, NEO4J_PORT)

        try:
            self._driver = AsyncGraphDatabase.driver(
                uri,
                auth=(NEO4J_USER, NEO4J_PASSWORD),
                max_connection_lifetime=NEO4J_MAX_CONNECTION_LIFETIME,
                max_connection_pool_size=NEO4J_MAX_CONNECTION_POOL_SIZE,
            )

            # Verify connectivity
            await self._driver.verify_connectivity()
            logger.info("Neo4j connection verified")

            # Create constraints and indexes
            await self._create_constraints()
            logger.info("Neo4j constraints created")
        except Exception as e:
            logger.warning("Neo4j connection failed: %s. Running in degraded mode.", e)
            self._driver = None

    async def close(self) -> None:
        """Close Neo4j connection"""
        if self._driver:
            try:
                await self._driver.close()
            except Exception:
                pass
            self._driver = None
        logger.debug("Neo4j connection closed")

    async def _create_constraints(self) -> None:
        """Create necessary constraints and indexes"""
        async with self._driver.session(database=NEO4J_DATABASE) as session:
            constraints = [
                "CREATE CONSTRAINT IF NOT EXISTS FOR (a:Attack) REQUIRE a.id IS UNIQUE",
                "CREATE CONSTRAINT IF NOT EXISTS FOR (t:Threat) REQUIRE t.id IS UNIQUE",
                "CREATE CONSTRAINT IF NOT EXISTS FOR (e:Entity) REQUIRE e.id IS UNIQUE",
                "CREATE CONSTRAINT IF NOT EXISTS FOR (i:Indicator) REQUIRE i.id IS UNIQUE",
                "CREATE CONSTRAINT IF NOT EXISTS FOR (p:Pattern) REQUIRE p.id IS UNIQUE",
                "CREATE INDEX IF NOT EXISTS FOR (a:Attack) ON (a.timestamp)",
                "CREATE INDEX IF NOT EXISTS FOR (a:Attack) ON (a.type)",
                "CREATE INDEX IF NOT EXISTS FOR (a:Attack) ON (a.severity)",
            ]
            for query in constraints:
                try:
                    await session.run(query)
                except Exception as e:
                    logger.warning("Neo4j constraint/index creation warning: %s", e)

    async def execute_query(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """Execute a Cypher query and return results"""
        if not self._driver:
            raise RuntimeError("Neo4j not initialized. Call initialize() first.")

        async with self._driver.session(database=NEO4J_DATABASE) as session:
            result = await session.run(query, **kwargs)
            records = await result.data()
            return records

    async def execute_write_query(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """Execute a write Cypher query in a write transaction"""
        if not self._driver:
            raise RuntimeError("Neo4j not initialized. Call initialize() first.")

        async with self._driver.session(database=NEO4J_DATABASE) as session:
            async with session.begin_transaction() as tx:
                result = await tx.run(query, **kwargs)
                records = await result.data()
                await tx.commit()
                return records

    @property
    def driver(self) -> Optional[AsyncDriver]:
        return self._driver

    @property
    def is_initialized(self) -> bool:
        return self._driver is not None


# Global singleton
neo4j_db = Neo4jDatabase()

