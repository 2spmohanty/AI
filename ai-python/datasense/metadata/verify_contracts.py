"""
metadata/verify_contracts.py

Run after load_contracts.py to confirm the graph is actually queryable the
way downstream code expects. This is the "gate" check before moving on to
the ingestion layer — don't proceed until this passes clean.

Usage:
    uv run python -m datasense.metadata.verify_contracts
"""

import os
from dotenv import load_dotenv

from datasense.metadata.neo4j_client import Neo4jClient
from datasense.metadata.schema_registry import get_dataset_schema

load_dotenv(os.path.join(os.path.dirname(__file__), "..", "infra", ".env"))


def main():
    client = Neo4jClient()
    if not client.verify_connectivity():
        print("FAIL: cannot connect to Neo4j.")
        return

    print("Connected to Neo4j.\n")

    for dataset_name in ["customer", "account", "transaction"]:
        schema = get_dataset_schema(dataset_name, client)
        print(f"--- {dataset_name} ---")
        print(f"  file_format: {schema.file_format}")
        print(f"  child_of: {schema.child_of}")
        print(f"  columns: {len(schema.columns)}")
        for col in schema.columns:
            fk_note = f" -> REFERENCES {col.references}" if col.references else ""
            print(f"    - {col.name} ({col.data_type}, nullable={col.nullable}){fk_note}")
        print(f"  business_rules: {len(schema.business_rules)}")
        for rule in schema.business_rules:
            print(f"    - {rule.name}: {rule.description}")
        print()

    # Explicit lineage check — this is the traversal the AI layer will
    # eventually rely on for cascade investigation, so confirm it works now
    lineage = client.run_read(
        "MATCH (t:Dataset)-[:CHILD_OF*]->(root:Dataset) "
        "RETURN t.name AS dataset, root.name AS ultimate_root"
    )
    print("--- lineage chains ---")
    for row in lineage:
        print(f"  {row['dataset']} -> ... -> {row['ultimate_root']}")

    client.close()
    print("\nOK: contracts loaded and queryable.")


if __name__ == "__main__":
    main()