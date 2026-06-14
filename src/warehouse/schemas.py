"""CSV schemas and local batch validation for warehouse loads."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ObjectSchema:
    file_name: str
    table_name: str
    primary_key: str
    columns: tuple[str, ...]


OBJECT_SCHEMAS: tuple[ObjectSchema, ...] = (
    ObjectSchema(
        file_name="customers.csv",
        table_name="customers",
        primary_key="customer_id",
        columns=(
            "customer_id",
            "customer_name",
            "customer_type",
            "industry",
            "segment",
            "company_size_band",
            "employee_count",
            "annual_revenue_band",
            "region",
            "state",
            "country",
            "acquisition_channel",
            "lifecycle_stage",
            "customer_health_score",
            "product_fit_score",
            "support_complexity_score",
            "price_sensitivity_score",
            "churn_risk_score",
            "start_date",
            "churned_at",
            "is_active",
            "batch_id",
            "created_at",
            "updated_at",
        ),
    ),
    ObjectSchema(
        file_name="contacts.csv",
        table_name="contacts",
        primary_key="contact_id",
        columns=(
            "contact_id",
            "customer_id",
            "first_name",
            "last_name",
            "email",
            "phone",
            "job_title",
            "department",
            "contact_role",
            "influence_level",
            "is_primary_contact",
            "created_at",
            "updated_at",
            "batch_id",
        ),
    ),
    ObjectSchema(
        file_name="employees.csv",
        table_name="employees",
        primary_key="employee_id",
        columns=(
            "employee_id",
            "manager_employee_id",
            "first_name",
            "last_name",
            "email",
            "department",
            "role",
            "region",
            "hire_date",
            "termination_date",
            "is_active",
            "performance_band",
            "capacity_band",
            "created_at",
            "updated_at",
            "batch_id",
        ),
    ),
    ObjectSchema(
        file_name="products.csv",
        table_name="products",
        primary_key="product_id",
        columns=(
            "product_id",
            "product_name",
            "product_family",
            "product_type",
            "complexity_level",
            "target_segment",
            "list_price_monthly",
            "list_price_annual",
            "launch_date",
            "retirement_date",
            "is_active",
            "created_at",
            "updated_at",
            "batch_id",
        ),
    ),
    ObjectSchema(
        file_name="opportunities.csv",
        table_name="opportunities",
        primary_key="opportunity_id",
        columns=(
            "opportunity_id",
            "customer_id",
            "primary_contact_id",
            "owner_employee_id",
            "product_id",
            "opportunity_name",
            "opportunity_type",
            "stage",
            "amount",
            "probability",
            "lead_source",
            "created_date",
            "expected_close_date",
            "closed_date",
            "is_won",
            "loss_reason",
            "created_at",
            "updated_at",
            "batch_id",
        ),
    ),
    ObjectSchema(
        file_name="contracts.csv",
        table_name="contracts",
        primary_key="contract_id",
        columns=(
            "contract_id",
            "customer_id",
            "product_id",
            "originating_opportunity_id",
            "owner_employee_id",
            "contract_status",
            "contract_type",
            "start_date",
            "end_date",
            "renewal_date",
            "contract_value",
            "billing_frequency",
            "auto_renew",
            "canceled_at",
            "cancellation_reason",
            "created_at",
            "updated_at",
            "batch_id",
        ),
    ),
    ObjectSchema(
        file_name="cases.csv",
        table_name="cases",
        primary_key="case_id",
        columns=(
            "case_id",
            "customer_id",
            "contract_id",
            "product_id",
            "owner_employee_id",
            "opened_by_contact_id",
            "case_type",
            "priority",
            "channel",
            "status",
            "opened_at",
            "first_response_at",
            "resolved_at",
            "resolution_category",
            "escalation_level",
            "satisfaction_score",
            "created_at",
            "updated_at",
            "batch_id",
        ),
    ),
    ObjectSchema(
        file_name="service_events.csv",
        table_name="service_events",
        primary_key="service_event_id",
        columns=(
            "service_event_id",
            "customer_id",
            "contact_id",
            "employee_id",
            "case_id",
            "contract_id",
            "product_id",
            "event_type",
            "event_direction",
            "event_channel",
            "event_at",
            "duration_minutes",
            "sentiment_score",
            "outcome_category",
            "created_at",
            "updated_at",
            "batch_id",
        ),
    ),
    ObjectSchema(
        file_name="outcomes.csv",
        table_name="outcomes",
        primary_key="outcome_id",
        columns=(
            "outcome_id",
            "customer_id",
            "contract_id",
            "related_case_id",
            "related_service_event_id",
            "outcome_type",
            "outcome_date",
            "outcome_status",
            "outcome_value",
            "renewal_flag",
            "churn_flag",
            "expansion_flag",
            "resolution_flag",
            "revenue_impact",
            "created_at",
            "updated_at",
            "batch_id",
        ),
    ),
)

SCHEMA_BY_FILE = {schema.file_name: schema for schema in OBJECT_SCHEMAS}
SCHEMA_BY_TABLE = {schema.table_name: schema for schema in OBJECT_SCHEMAS}
RAW_METADATA_COLUMNS = ("row_hash", "loaded_at", "source_file_name")


@dataclass(frozen=True)
class BatchFile:
    path: Path
    schema: ObjectSchema
    row_count: int


@dataclass(frozen=True)
class LocalBatchValidation:
    batch_id: str
    batch_dir: Path
    files: tuple[BatchFile, ...]


def batch_dir_for(batch_id: str, source_root: str | Path = "data/generated") -> Path:
    return Path(source_root) / batch_id


def detected_csv_files(batch_dir: Path) -> list[Path]:
    return sorted(path for path in batch_dir.glob("*.csv") if path.is_file())


def read_header(path: Path) -> list[str]:
    with path.open(newline="") as csv_file:
        reader = csv.reader(csv_file)
        try:
            return next(reader)
        except StopIteration as exc:
            raise ValueError(f"{path} is empty") from exc


def count_rows(path: Path) -> int:
    with path.open(newline="") as csv_file:
        reader = csv.reader(csv_file)
        next(reader, None)
        return sum(1 for _ in reader)


def validate_local_batch(
    batch_id: str,
    source_root: str | Path = "data/generated",
) -> LocalBatchValidation:
    batch_dir = batch_dir_for(batch_id, source_root)
    if not batch_dir.exists():
        raise FileNotFoundError(f"Batch directory does not exist: {batch_dir}")

    files = detected_csv_files(batch_dir)
    if not files:
        raise ValueError(f"No CSV files found in batch directory: {batch_dir}")

    batch_files: list[BatchFile] = []
    for path in files:
        schema = SCHEMA_BY_FILE.get(path.name)
        if schema is None:
            known = ", ".join(sorted(SCHEMA_BY_FILE))
            raise ValueError(f"Unknown CSV file {path.name}; expected one of: {known}")

        header = read_header(path)
        expected_header = list(schema.columns)
        if header != expected_header:
            raise ValueError(
                f"Schema mismatch in {path}: expected {expected_header}, got {header}"
            )

        seen_keys: set[str] = set()
        duplicate_keys: set[str] = set()
        blank_keys = 0
        wrong_batch = 0
        with path.open(newline="") as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                primary_key = row[schema.primary_key]
                if not primary_key:
                    blank_keys += 1
                elif primary_key in seen_keys:
                    duplicate_keys.add(primary_key)
                else:
                    seen_keys.add(primary_key)
                if row.get("batch_id") != batch_id:
                    wrong_batch += 1

        if blank_keys:
            raise ValueError(f"{path} has {blank_keys} blank primary keys")
        if duplicate_keys:
            examples = ", ".join(sorted(duplicate_keys)[:5])
            raise ValueError(f"{path} has duplicate primary keys: {examples}")
        if wrong_batch:
            raise ValueError(f"{path} has {wrong_batch} rows with unexpected batch_id")

        batch_files.append(BatchFile(path=path, schema=schema, row_count=count_rows(path)))

    return LocalBatchValidation(
        batch_id=batch_id,
        batch_dir=batch_dir,
        files=tuple(batch_files),
    )

