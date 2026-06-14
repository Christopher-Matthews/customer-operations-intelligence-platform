"""Validate local CSV batches and BigQuery staging loads."""

from __future__ import annotations

from dataclasses import dataclass

from warehouse.config import get_bigquery_client, load_warehouse_config
from warehouse.schemas import ObjectSchema, validate_local_batch


@dataclass(frozen=True)
class StagingValidationResult:
    table_name: str
    local_rows: int
    staging_rows: int
    duplicate_primary_keys: int
    blank_primary_keys: int
    wrong_batch_rows: int


def validate_staging_load(
    env: str,
    batch_id: str,
    source_root: str = "data/generated",
    confirm_prod: bool = False,
) -> list[StagingValidationResult]:
    from google.cloud import bigquery

    config = load_warehouse_config(env=env, confirm_prod=confirm_prod)
    client = get_bigquery_client(config)
    validation = validate_local_batch(batch_id=batch_id, source_root=source_root)

    results: list[StagingValidationResult] = []
    for batch_file in validation.files:
        table_id = f"{config.project_id}.{config.staging_dataset}.{batch_file.schema.table_name}"
        table = client.get_table(table_id)
        _validate_table_columns(batch_file.schema, table)

        staging_rows = _scalar_query(
            client,
            f"SELECT COUNT(*) FROM `{table_id}`",
        )
        duplicate_primary_keys = _scalar_query(
            client,
            f"""
            SELECT COUNT(*)
            FROM (
              SELECT `{batch_file.schema.primary_key}`
              FROM `{table_id}`
              GROUP BY `{batch_file.schema.primary_key}`
              HAVING COUNT(*) > 1
            )
            """,
        )
        blank_primary_keys = _scalar_query(
            client,
            f"""
            SELECT COUNT(*)
            FROM `{table_id}`
            WHERE `{batch_file.schema.primary_key}` IS NULL
               OR `{batch_file.schema.primary_key}` = ''
            """,
        )
        wrong_batch_rows = _scalar_query(
            client,
            f"""
            SELECT COUNT(*)
            FROM `{table_id}`
            WHERE `batch_id` IS NULL OR `batch_id` != @batch_id
            """,
            [bigquery.ScalarQueryParameter("batch_id", "STRING", batch_id)],
        )

        result = StagingValidationResult(
            table_name=batch_file.schema.table_name,
            local_rows=batch_file.row_count,
            staging_rows=staging_rows,
            duplicate_primary_keys=duplicate_primary_keys,
            blank_primary_keys=blank_primary_keys,
            wrong_batch_rows=wrong_batch_rows,
        )
        _raise_if_invalid(result)
        results.append(result)

    return results


def _validate_table_columns(schema: ObjectSchema, table) -> None:
    actual_columns = [field.name for field in table.schema]
    expected_columns = list(schema.columns)
    if actual_columns != expected_columns:
        raise ValueError(
            f"Staging table {schema.table_name} schema mismatch: "
            f"expected {expected_columns}, got {actual_columns}"
        )


def _raise_if_invalid(result: StagingValidationResult) -> None:
    if result.staging_rows != result.local_rows:
        raise ValueError(
            f"{result.table_name}: staging row count {result.staging_rows} "
            f"does not match local row count {result.local_rows}"
        )
    if result.duplicate_primary_keys:
        raise ValueError(
            f"{result.table_name}: {result.duplicate_primary_keys} duplicate primary keys"
        )
    if result.blank_primary_keys:
        raise ValueError(f"{result.table_name}: {result.blank_primary_keys} blank primary keys")
    if result.wrong_batch_rows:
        raise ValueError(
            f"{result.table_name}: {result.wrong_batch_rows} rows do not match requested batch_id"
        )


def _scalar_query(client, sql: str, query_parameters=None) -> int:
    from google.cloud import bigquery

    job_config = None
    if query_parameters:
        job_config = bigquery.QueryJobConfig(query_parameters=query_parameters)
    rows = list(client.query(sql, job_config=job_config).result())
    return int(rows[0][0])

