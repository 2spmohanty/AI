"""
metadata/load_contracts.py

Run this once to load dataset contracts into Neo4j. Safe to re-run after
editing contracts.py — every write uses MERGE, so existing nodes are updated
in place rather than duplicated.

Usage:
    python -m metadata.load_contracts

Graph shape produced:
    (:Dataset {name, description, file_format})
    (:Dataset)-[:HAS_COLUMN]->(:Column {name, dataset, data_type, nullable,
                                          is_primary_key, is_foreign_key,
                                          allowed_values, min_value, max_value,
                                          description})
    (:Dataset)-[:HAS_RULE]->(:BusinessRule {name, description, rule_type,
                                             applies_to_column,
                                             condition_column, condition_equals})
    (:Column)-[:REFERENCES]->(:Column)      -- foreign key edges
    (:Dataset)-[:CHILD_OF]->(:Dataset)      -- lineage edges (Account CHILD_OF Customer, etc.)

No AI touches this step. Pure schema definition, per the original design brief.
"""

import os
from dotenv import load_dotenv

from datasense.metadata.neo4j_client import Neo4jClient
from datasense.metadata.contracts import ALL_CONTRACTS

# infra/.env holds NEO4J_URI / NEO4J_USER / NEO4J_PASSWORD, scoped to this project
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "infra", ".env"))


def load_dataset_node(client: Neo4jClient, contract) -> None:
    client.run_write(
        """
        MERGE (d:Dataset {name: $name})
        SET d.description = $description,
            d.file_format = $file_format
        """,
        {
            "name": contract.name,
            "description": contract.description,
            "file_format": contract.file_format,
        },
    )


def load_columns(client: Neo4jClient, contract) -> None:
    for col in contract.columns:
        client.run_write(
            """
            MATCH (d:Dataset {name: $dataset})
            MERGE (c:Column {dataset: $dataset, name: $name})
            SET c.data_type = $data_type,
                c.nullable = $nullable,
                c.is_primary_key = $is_primary_key,
                c.is_foreign_key = $is_foreign_key,
                c.allowed_values = $allowed_values,
                c.min_value = $min_value,
                c.max_value = $max_value,
                c.description = $description
            MERGE (d)-[:HAS_COLUMN]->(c)
            """,
            {
                "dataset": contract.name,
                "name": col.name,
                "data_type": col.data_type,
                "nullable": col.nullable,
                "is_primary_key": col.is_primary_key,
                "is_foreign_key": col.is_foreign_key,
                "allowed_values": col.allowed_values,
                "min_value": col.min_value,
                "max_value": col.max_value,
                "description": col.description,
            },
        )


def load_business_rules(client: Neo4jClient, contract) -> None:
    for rule in contract.business_rules:
        client.run_write(
            """
            MATCH (d:Dataset {name: $dataset})
            MERGE (r:BusinessRule {dataset: $dataset, name: $name})
            SET r.description = $description,
                r.rule_type = $rule_type,
                r.applies_to_column = $applies_to_column,
                r.condition_column = $condition_column,
                r.condition_equals = $condition_equals
            MERGE (d)-[:HAS_RULE]->(r)
            """,
            {
                "dataset": contract.name,
                "name": rule.name,
                "description": rule.description,
                "rule_type": rule.rule_type,
                "applies_to_column": rule.applies_to_column,
                "condition_column": rule.condition_column,
                "condition_equals": rule.condition_equals,
            },
        )


def load_foreign_key_edges(client: Neo4jClient, contract) -> None:
    for col in contract.columns:
        if col.is_foreign_key and col.references:
            ref_dataset, ref_column = col.references.split(".")
            client.run_write(
                """
                MATCH (source:Column {dataset: $source_dataset, name: $source_column})
                MATCH (target:Column {dataset: $ref_dataset, name: $ref_column})
                MERGE (source)-[:REFERENCES]->(target)
                """,
                {
                    "source_dataset": contract.name,
                    "source_column": col.name,
                    "ref_dataset": ref_dataset,
                    "ref_column": ref_column,
                },
            )


def load_lineage_edges(client: Neo4jClient, contract) -> None:
    if contract.child_of:
        client.run_write(
            """
            MATCH (child:Dataset {name: $child})
            MATCH (parent:Dataset {name: $parent})
            MERGE (child)-[:CHILD_OF]->(parent)
            """,
            {"child": contract.name, "parent": contract.child_of},
        )


def main():
    client = Neo4jClient()
    if not client.verify_connectivity():
        raise ConnectionError(
            "Cannot reach Neo4j. Is the container running? "
            "Check: docker-compose ps (from infra/)"
        )

    print("Connected to Neo4j. Loading contracts...")

    # Pass 1: datasets + columns + rules (no cross-dataset edges yet)
    for contract in ALL_CONTRACTS:
        load_dataset_node(client, contract)
        load_columns(client, contract)
        load_business_rules(client, contract)
        print(f"  loaded dataset + columns + rules: {contract.name}")

    # Pass 2: cross-dataset edges — must run after ALL Column nodes exist,
    # since FK edges reference columns in other datasets
    for contract in ALL_CONTRACTS:
        load_foreign_key_edges(client, contract)
        load_lineage_edges(client, contract)
        print(f"  loaded relationships for: {contract.name}")

    client.close()
    print("Done. Contracts loaded into Neo4j.")


if __name__ == "__main__":
    main()