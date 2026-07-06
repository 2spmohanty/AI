"""
ingestion/generator.py

Two responsibilities, kept strictly separate:

1. generate_rows()   — produce clean, contract-valid synthetic rows via Faker,
                        with FK-aware sampling for positive scenarios.
2. inject_anomaly()  — take already-generated rows and corrupt them according
                        to one of 7 error types, targeting a RANDOM eligible
                        column when target_column isn't explicitly forced.

Nothing in this file talks to SQLite, Neo4j connections, or MQTT — it only
consumes a DatasetSchema object (from schema_registry.py) that the caller
(ingestion_engine.py) already fetched. Keeps this module pure and testable.
"""

import random
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional

import numpy as np
from faker import Faker

from datasense.metadata.schema_registry import DatasetSchema

fake = Faker()


# ---------------------------------------------------------------------------
# Row generation
# ---------------------------------------------------------------------------

def _generate_pk(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:10].upper()}"


def _generate_customer_row() -> dict:
    return {
        "customer_id": _generate_pk("CUST"),
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "email": fake.unique.email(),
        "signup_date": fake.date_between(start_date="-3y", end_date="today").isoformat(),
        "country": random.choice(["AU", "US", "UK", "NZ", "SG"]),
        # customer_segment is nullable=True in the contract — ~25% naturally
        # absent. This is NOT an anomaly injection, just realistic optionality.
        "customer_segment": random.choice(
            ["RETAIL", "PREMIUM", "BUSINESS", None, None]
        ),
    }


def _generate_account_row(customer_id: str) -> dict:
    return {
        "account_id": _generate_pk("ACC"),
        "customer_id": customer_id,
        "account_type": random.choice(["CHECKING", "SAVINGS", "CREDIT"]),
        "opened_date": fake.date_between(start_date="-3y", end_date="today").isoformat(),
        "status": random.choice(["ACTIVE", "ACTIVE", "ACTIVE", "CLOSED", "FROZEN"]),
        "balance": round(float(np.random.uniform(0, 50000)), 2),
    }


def _generate_transaction_row(account_id: str) -> dict:
    transaction_type = random.choice(["DEPOSIT", "WITHDRAWAL", "TRANSFER", "FEE"])
    # Amount sign/magnitude coupled to type — matches the business rule that
    # DEPOSIT must be positive, and keeps the other types realistic so that
    # a negative_amount injection on DEPOSIT is a genuine, meaningful anomaly
    # rather than indistinguishable background noise.
    if transaction_type == "DEPOSIT":
        amount = round(float(np.random.uniform(10, 5000)), 2)
    elif transaction_type == "WITHDRAWAL":
        amount = round(float(-np.random.uniform(10, 3000)), 2)
    elif transaction_type == "FEE":
        amount = round(float(-np.random.uniform(1, 50)), 2)
    else:  # TRANSFER — can be inbound or outbound
        amount = round(float(np.random.uniform(-3000, 3000)), 2)

    txn_datetime = datetime.now() - timedelta(
        days=random.randint(0, 30), hours=random.randint(0, 23)
    )
    return {
        "transaction_id": _generate_pk("TXN"),
        "account_id": account_id,
        "transaction_type": transaction_type,
        "amount": amount,
        "transaction_date": txn_datetime.isoformat(),
        "currency": random.choice(["AUD", "USD", "EUR"]),
    }


def generate_rows(
    dataset_name: str,
    schema: DatasetSchema,
    row_count: int,
    fk_pool: Optional[list] = None,
) -> list[dict]:
    """
    fk_pool: list of upstream PK values to sample from (with replacement) for
    the FK column. Required for 'account' (customer_id) and 'transaction'
    (account_id). Ignored for 'customer', which has no FK.
    """
    if dataset_name == "customer":
        return [_generate_customer_row() for _ in range(row_count)]

    if dataset_name == "account":
        if not fk_pool:
            raise ValueError("account generation requires a non-empty fk_pool of customer_id values")
        return [_generate_account_row(random.choice(fk_pool)) for _ in range(row_count)]

    if dataset_name == "transaction":
        if not fk_pool:
            raise ValueError("transaction generation requires a non-empty fk_pool of account_id values")
        return [_generate_transaction_row(random.choice(fk_pool)) for _ in range(row_count)]

    raise ValueError(f"Unknown dataset: {dataset_name}")


# ---------------------------------------------------------------------------
# Anomaly injection
# ---------------------------------------------------------------------------

@dataclass
class InjectionResult:
    rows: list[dict]
    tier: int
    error_type: str
    target_column: Optional[str]
    actual_rows_affected: int
    description: str


def _sample_indices(n_total: int, error_pct: float, rng: random.Random) -> list[int]:
    n_affected = round(n_total * error_pct / 100)
    n_affected = min(n_affected, n_total)
    return rng.sample(range(n_total), n_affected) if n_affected > 0 else []


def inject_null_spike(rows, schema: DatasetSchema, error_pct, target_column, rng) -> InjectionResult:
    eligible = [c.name for c in schema.columns if not c.nullable]
    if not eligible:
        raise ValueError(f"No non-nullable columns available for null_spike on {schema.name}")
    if target_column and target_column not in eligible:
        raise ValueError(f"'{target_column}' is not a non-nullable column on {schema.name}")
    col = target_column or rng.choice(eligible)

    indices = _sample_indices(len(rows), error_pct, rng)
    for i in indices:
        rows[i][col] = None

    return InjectionResult(
        rows=rows, tier=1, error_type="null_spike", target_column=col,
        actual_rows_affected=len(indices),
        description=f"Injected null into '{col}' for {len(indices)}/{len(rows)} rows "
                    f"({error_pct}% requested)",
    )


def inject_negative_amount(rows, schema: DatasetSchema, error_pct, target_column, rng) -> InjectionResult:
    positive_rules = [r for r in schema.business_rules if r.rule_type == "positive"]
    if not positive_rules:
        raise ValueError(f"No 'positive' business rule defined for {schema.name}")
    rule = positive_rules[0]
    col = rule.applies_to_column

    if rule.condition_column:
        eligible_indices = [
            i for i, row in enumerate(rows)
            if row.get(rule.condition_column) == rule.condition_equals
        ]
    else:
        eligible_indices = list(range(len(rows)))

    n_affected = min(round(len(eligible_indices) * error_pct / 100), len(eligible_indices))
    chosen = rng.sample(eligible_indices, n_affected) if n_affected > 0 else []
    for i in chosen:
        rows[i][col] = -abs(rows[i][col])

    condition_note = f" where {rule.condition_column}={rule.condition_equals}" if rule.condition_column else ""
    return InjectionResult(
        rows=rows, tier=1, error_type="negative_amount", target_column=col,
        actual_rows_affected=len(chosen),
        description=f"Forced '{col}' negative for {len(chosen)} rows{condition_note} "
                    f"({error_pct}% requested)",
    )


def inject_orphan_fk(rows, schema: DatasetSchema, error_pct, target_column, rng) -> InjectionResult:
    fk_cols = [c.name for c in schema.columns if c.is_foreign_key]
    if not fk_cols:
        raise ValueError(f"{schema.name} has no foreign key columns")
    if target_column and target_column not in fk_cols:
        raise ValueError(f"'{target_column}' is not a foreign key column on {schema.name}")
    col = target_column or rng.choice(fk_cols)

    indices = _sample_indices(len(rows), error_pct, rng)
    for i in indices:
        rows[i][col] = f"ORPHAN-{uuid.uuid4().hex[:8].upper()}"

    return InjectionResult(
        rows=rows, tier=2, error_type="orphan_fk", target_column=col,
        actual_rows_affected=len(indices),
        description=f"Replaced '{col}' with non-existent IDs for {len(indices)}/{len(rows)} rows "
                    f"({error_pct}% requested) — orphaned, no matching parent",
    )


def inject_schema_rename(rows, schema: DatasetSchema, error_pct, target_column, rng) -> InjectionResult:
    # error_pct intentionally ignored — a rename either happened to the whole
    # file or it didn't. Kept in the signature only for dispatch uniformity.
    all_cols = [c.name for c in schema.columns]
    col = target_column or rng.choice(all_cols)
    new_name = f"{col}_v2" if not col.endswith("_id") else col.replace("_id", "_identifier")

    for row in rows:
        row[new_name] = row.pop(col)

    return InjectionResult(
        rows=rows, tier=3, error_type="schema_rename", target_column=col,
        actual_rows_affected=len(rows),
        description=f"Renamed column '{col}' -> '{new_name}' across entire file "
                    f"(unannounced schema drift)",
    )


def inject_schema_type_change(rows, schema: DatasetSchema, error_pct, target_column, rng) -> InjectionResult:
    # error_pct ignored, same reasoning as inject_schema_rename.
    numeric_cols = [c.name for c in schema.columns
                    if c.data_type in ("INTEGER", "FLOAT") and not c.is_primary_key]
    eligible = numeric_cols or [c.name for c in schema.columns if not c.is_primary_key]
    if target_column and target_column not in eligible:
        raise ValueError(f"'{target_column}' is not eligible for type-change on {schema.name}")
    col = target_column or rng.choice(eligible)

    if schema.file_format == "json":
        # JSON preserves type distinction natively — a quoted "123.45" is
        # genuinely a different type than a bare 123.45. str() alone is a
        # real, detectable drift here.
        for row in rows:
            row[col] = str(row[col])
        detail = "quoted numeric as JSON string"
    else:
        # CSV is all-text regardless — str(123.45) round-trips back to a
        # float on read, silently defeating the anomaly. Corrupt it into
        # something that genuinely can't parse as numeric, so pandas is
        # forced to infer dtype=object instead of float/int.
        for row in rows:
            row[col] = f"{row[col]}_CORRUPT"
        detail = "appended non-numeric suffix, forcing dtype=object on read"

    return InjectionResult(
        rows=rows, tier=3, error_type="schema_type_change", target_column=col,
        actual_rows_affected=len(rows),
        description=f"Changed data type of '{col}' ({detail}) — contract declares it numeric",
    )


def inject_volume_drop(rows, schema: DatasetSchema, error_pct, target_column, rng) -> InjectionResult:
    n_keep = max(0, len(rows) - round(len(rows) * error_pct / 100))
    dropped = len(rows) - n_keep
    kept_rows = rng.sample(rows, n_keep) if n_keep < len(rows) else rows

    return InjectionResult(
        rows=kept_rows, tier=4, error_type="volume_drop", target_column=None,
        actual_rows_affected=dropped,
        description=f"Dropped {dropped}/{len(rows)} rows ({error_pct}% requested) "
                    f"— only detectable via historical row-count baseline comparison",
    )


def inject_statistical_drift(rows, schema: DatasetSchema, error_pct, target_column, rng) -> InjectionResult:
    numeric_cols = [c.name for c in schema.columns
                    if c.data_type in ("FLOAT", "INTEGER")
                    and not c.is_primary_key and not c.is_foreign_key]
    if not numeric_cols:
        raise ValueError(f"No numeric non-key columns available for statistical_drift on {schema.name}")
    if target_column and target_column not in numeric_cols:
        raise ValueError(f"'{target_column}' is not eligible for statistical_drift on {schema.name}")
    col = target_column or rng.choice(numeric_cols)

    multiplier = round(float(np.random.uniform(5, 10)), 2)
    indices = _sample_indices(len(rows), error_pct, rng)
    for i in indices:
        rows[i][col] = round(rows[i][col] * multiplier, 2)

    return InjectionResult(
        rows=rows, tier=5, error_type="statistical_drift", target_column=col,
        actual_rows_affected=len(indices),
        description=f"Applied {multiplier}x multiplier to '{col}' for {len(indices)}/{len(rows)} rows "
                    f"— individually plausible values, only visible against a historical baseline",
    )


ANOMALY_REGISTRY = {
    "null_spike": inject_null_spike,
    "negative_amount": inject_negative_amount,
    "orphan_fk": inject_orphan_fk,
    "schema_rename": inject_schema_rename,
    "schema_type_change": inject_schema_type_change,
    "volume_drop": inject_volume_drop,
    "statistical_drift": inject_statistical_drift,
}


def inject_anomaly(
    error_type: str,
    rows: list[dict],
    schema: DatasetSchema,
    error_pct: float = 0.0,
    target_column: Optional[str] = None,
    seed: Optional[int] = None,
) -> InjectionResult:
    if error_type not in ANOMALY_REGISTRY:
        raise ValueError(
            f"Unknown error_type '{error_type}'. Valid options: {list(ANOMALY_REGISTRY)}"
        )
    rng = random.Random(seed) if seed is not None else random
    return ANOMALY_REGISTRY[error_type](rows, schema, error_pct, target_column, rng)