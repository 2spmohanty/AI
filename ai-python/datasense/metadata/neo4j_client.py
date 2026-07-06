"""
metadata/neo4j_client.py

Thin wrapper around the official neo4j Python driver. Nothing clever here on
purpose — this is infrastructure plumbing, not a place for business logic.
Reads connection details from environment variables, expected to be loaded
from infra/.env (NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD).
"""

import os
from neo4j import GraphDatabase


class Neo4jClient:
    def __init__(self, uri: str = None, user: str = None, password: str = None):
        self._uri = uri or os.environ.get("NEO4J_URI", "bolt://localhost:7687")
        self._user = user or os.environ.get("NEO4J_USER", "neo4j")
        self._password = password or os.environ.get("NEO4J_PASSWORD", "datasense123")
        self._driver = GraphDatabase.driver(self._uri, auth=(self._user, self._password))

    def close(self):
        self._driver.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def run_write(self, query: str, parameters: dict = None) -> list[dict]:
        with self._driver.session() as session:
            result = session.execute_write(lambda tx: list(tx.run(query, parameters or {})))
            return [record.data() for record in result]

    def run_read(self, query: str, parameters: dict = None) -> list[dict]:
        with self._driver.session() as session:
            result = session.execute_read(lambda tx: list(tx.run(query, parameters or {})))
            return [record.data() for record in result]

    def verify_connectivity(self) -> bool:
        try:
            self._driver.verify_connectivity()
            return True
        except Exception:
            return False