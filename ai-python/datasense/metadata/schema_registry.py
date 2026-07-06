"""
metadata/schema_registry.py

Runtime read API. This is the ONLY module `generator.py`, `ingestion_engine.py`,
and `dq_pipeline.py` should import to answer "what does this dataset look
like". Everything here queries Neo4j live — nothing is cached from
contracts.py. This matters: if the AI-layer mentorship phase later has you
build a tool for the agent to "check the schema," this is the function it
should call under the hood, guaranteeing the agent sees exactly the same
schema of truth as the deterministic layer, not a stale Python copy.
"""

from dataclasses import dataclass
from typing import Optional

from datasense.metadata.neo4j_client import Neo4jClient


@dataclass
class ColumnDefinition:
    name: str
    data_type: str
    nullable: bool
    is_primary_key: bool
    is_foreign_key: bool
    allowed_values: Optional[list]
    min_value: Optional[float]
    max_value: Optional[float]
    description: str
    references: Optional[str] = None   # populated separately via REFERENCES edge


@dataclass
class BusinessRuleDefinition:
    name: str
    description: str
    rule_type: str
    applies_to_column: Optional[str]
    condition_column: Optional[str]
    condition_equals: Optional[str]


@dataclass
class DatasetSchema:
    name: str
    description: str
    file_format: str
    columns: list[ColumnDefinition]
    business_rules: list[BusinessRuleDefinition]
    child_of: Optional[str]


def get_dataset_schema(dataset_name: str, client: Neo4jClient = None) -> DatasetSchema:
    """
    Fetch the full contract for a dataset directly from Neo4j.
    Opens its own client if one isn't passed in, closes it before returning.
    """
    owns_client = client is None
    client = client or Neo4jClient()
    try:
        dataset_rows = client.run_read(
            "MATCH (d:Dataset {name: $name}) RETURN d.description AS description, "
            "d.file_format AS file_format",
            {"name": dataset_name},
        )
        if not dataset_rows:
            raise ValueError(f"No dataset contract found in Neo4j for '{dataset_name}'")

        column_rows = client.run_read(
            """
            MATCH (d:Dataset {name: $name})-[:HAS_COLUMN]->(c:Column)
            OPTIONAL MATCH (c)-[:REFERENCES]->(ref:Column)
            RETURN c.name AS name, c.data_type AS data_type, c.nullable AS nullable,
                   c.is_primary_key AS is_primary_key, c.is_foreign_key AS is_foreign_key,
                   c.allowed_values AS allowed_values, c.min_value AS min_value,
                   c.max_value AS max_value, c.description AS description,
                   ref.dataset AS ref_dataset, ref.name AS ref_column
            """,
            {"name": dataset_name},
        )

        rule_rows = client.run_read(
            """
            MATCH (d:Dataset {name: $name})-[:HAS_RULE]->(r:BusinessRule)
            RETURN r.name AS name, r.description AS description, r.rule_type AS rule_type,
                   r.applies_to_column AS applies_to_column,
                   r.condition_column AS condition_column,
                   r.condition_equals AS condition_equals
            """,
            {"name": dataset_name},
        )

        lineage_rows = client.run_read(
            "MATCH (d:Dataset {name: $name})-[:CHILD_OF]->(parent:Dataset) "
            "RETURN parent.name AS parent",
            {"name": dataset_name},
        )

        columns = []
        for row in column_rows:
            reference = None
            if row["ref_dataset"] and row["ref_column"]:
                reference = f"{row['ref_dataset']}.{row['ref_column']}"
            columns.append(ColumnDefinition(
                name=row["name"], data_type=row["data_type"], nullable=row["nullable"],
                is_primary_key=row["is_primary_key"], is_foreign_key=row["is_foreign_key"],
                allowed_values=row["allowed_values"], min_value=row["min_value"],
                max_value=row["max_value"], description=row["description"],
                references=reference,
            ))

        business_rules = [
            BusinessRuleDefinition(
                name=row["name"], description=row["description"], rule_type=row["rule_type"],
                applies_to_column=row["applies_to_column"],
                condition_column=row["condition_column"],
                condition_equals=row["condition_equals"],
            )
            for row in rule_rows
        ]

        return DatasetSchema(
            name=dataset_name,
            description=dataset_rows[0]["description"],
            file_format=dataset_rows[0]["file_format"],
            columns=columns,
            business_rules=business_rules,
            child_of=lineage_rows[0]["parent"] if lineage_rows else None,
        )
    finally:
        if owns_client:
            client.close()


def get_foreign_key_columns(dataset_name: str, client: Neo4jClient = None) -> list[ColumnDefinition]:
    """Convenience filter — used by generator.py to know which columns need FK sampling."""
    schema = get_dataset_schema(dataset_name, client)
    return [c for c in schema.columns if c.is_foreign_key]


def get_nullable_eligible_columns(dataset_name: str, client: Neo4jClient = None) -> list[str]:
    """
    Columns eligible for null-spike injection = declared non-nullable columns.
    Injecting nulls into an already-nullable column isn't a violation, so it's
    excluded here on purpose — Tier 1 error injection should pick from this list.
    """
    schema = get_dataset_schema(dataset_name, client)
    return [c.name for c in schema.columns if not c.nullable]