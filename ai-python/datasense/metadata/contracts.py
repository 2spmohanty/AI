"""
metadata/contracts.py

This is the AUTHORING layer for dataset contracts — plain Python, version
controlled, human-edited. It is NOT what the ingestion/DQ/AI code reads at
runtime. `load_contracts.py` reads this file ONCE and writes it into Neo4j.
From that point on, `schema_registry.py` is the only runtime path anyone
should use to ask "what does this dataset look like" — always via Neo4j,
never by re-importing this file. That indirection is deliberate: it forces
every part of the system (including, later, the AI agent) to treat Neo4j as
the actual schema of truth, not a Python file.

To change the contract: edit this file, re-run load_contracts.py. The load
is idempotent (MERGE-based) so re-running it after a change is always safe.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Column:
    name: str
    data_type: str            # STRING | INTEGER | FLOAT | DATE | DATETIME | BOOLEAN
    nullable: bool = True
    is_primary_key: bool = False
    is_foreign_key: bool = False
    references: Optional[str] = None   # "Dataset.column", e.g. "customer.customer_id"
    allowed_values: Optional[list] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    description: str = ""


@dataclass
class BusinessRule:
    name: str
    description: str
    # Optional row-conditional hint for later GE checkpoint construction, e.g.
    # a rule that only applies "when transaction_type == DEPOSIT". Left as a
    # loosely structured dict rather than executable code — Neo4j stores data,
    # not logic. The DQ layer interprets this at runtime.
    condition_column: Optional[str] = None
    condition_equals: Optional[str] = None
    applies_to_column: Optional[str] = None
    rule_type: str = "range"   # range | positive | non_null | categorical


@dataclass
class DatasetContract:
    name: str
    description: str
    file_format: str                      # csv | json
    columns: list[Column] = field(default_factory=list)
    business_rules: list[BusinessRule] = field(default_factory=list)
    child_of: Optional[str] = None        # parent dataset name, for lineage traversal


CUSTOMER = DatasetContract(
    name="customer",
    description="Root entity — individual banking customers",
    file_format="csv",
    columns=[
        Column("customer_id", "STRING", nullable=False, is_primary_key=True,
               description="Unique customer identifier"),
        Column("first_name", "STRING", nullable=False),
        Column("last_name", "STRING", nullable=False),
        Column("email", "STRING", nullable=False),
        Column("signup_date", "DATE", nullable=False),
        Column("country", "STRING", nullable=False,
               allowed_values=["AU", "US", "UK", "NZ", "SG"]),
        Column("customer_segment", "STRING", nullable=True,
               allowed_values=["RETAIL", "PREMIUM", "BUSINESS"]),
    ],
    business_rules=[
        BusinessRule(
            name="customer_id_not_null",
            description="customer_id must never be null",
            applies_to_column="customer_id",
            rule_type="non_null",
        ),
        BusinessRule(
            name="country_categorical",
            description="country must be one of the declared allowed values",
            applies_to_column="country",
            rule_type="categorical",
        ),
    ],
)

ACCOUNT = DatasetContract(
    name="account",
    description="Bank accounts, one customer may hold several",
    file_format="csv",
    child_of="customer",
    columns=[
        Column("account_id", "STRING", nullable=False, is_primary_key=True,
               description="Unique account identifier"),
        Column("customer_id", "STRING", nullable=False, is_foreign_key=True,
               references="customer.customer_id",
               description="FK to owning customer"),
        Column("account_type", "STRING", nullable=False,
               allowed_values=["CHECKING", "SAVINGS", "CREDIT"]),
        Column("opened_date", "DATE", nullable=False),
        Column("status", "STRING", nullable=False,
               allowed_values=["ACTIVE", "CLOSED", "FROZEN"]),
        Column("balance", "FLOAT", nullable=False, min_value=0.0),
    ],
    business_rules=[
        BusinessRule(
            name="account_id_not_null",
            description="account_id must never be null",
            applies_to_column="account_id",
            rule_type="non_null",
        ),
        BusinessRule(
            name="customer_id_fk_not_null",
            description="customer_id must never be null (required for FK integrity)",
            applies_to_column="customer_id",
            rule_type="non_null",
        ),
        BusinessRule(
            name="balance_non_negative",
            description="balance must be >= 0",
            applies_to_column="balance",
            rule_type="range",
        ),
    ],
)

TRANSACTION = DatasetContract(
    name="transaction",
    description="Financial transactions posted against an account",
    file_format="json",
    child_of="account",
    columns=[
        Column("transaction_id", "STRING", nullable=False, is_primary_key=True),
        Column("account_id", "STRING", nullable=False, is_foreign_key=True,
               references="account.account_id",
               description="FK to owning account"),
        Column("transaction_type", "STRING", nullable=False,
               allowed_values=["DEPOSIT", "WITHDRAWAL", "TRANSFER", "FEE"]),
        Column("amount", "FLOAT", nullable=False),
        Column("transaction_date", "DATETIME", nullable=False),
        Column("currency", "STRING", nullable=False,
               allowed_values=["AUD", "USD", "EUR"]),
    ],
    business_rules=[
        BusinessRule(
            name="transaction_id_not_null",
            description="transaction_id must never be null",
            applies_to_column="transaction_id",
            rule_type="non_null",
        ),
        BusinessRule(
            name="account_id_fk_not_null",
            description="account_id must never be null (required for FK integrity)",
            applies_to_column="account_id",
            rule_type="non_null",
        ),
        BusinessRule(
            name="deposit_amount_positive",
            description="amount must be positive when transaction_type = DEPOSIT",
            applies_to_column="amount",
            condition_column="transaction_type",
            condition_equals="DEPOSIT",
            rule_type="positive",
        ),
    ],
)

ALL_CONTRACTS: list[DatasetContract] = [CUSTOMER, ACCOUNT, TRANSACTION]