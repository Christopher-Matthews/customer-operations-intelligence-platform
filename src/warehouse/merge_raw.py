"""Append new hash-versioned rows from staging into BigQuery raw tables."""

from __future__ import annotations

from dataclasses import dataclass

from warehouse.config import get_bigquery_client, load_warehouse_config
from warehouse.schemas import RAW_METADATA_COLUMNS, ObjectSchema, validate_local_batch
from warehouse.validate_load import validate_staging_load


@dataclass(frozen=True)
class RawAppendResult:
    table_name: str
    rows_before: int
    rows_after: int
    inserted_rows: int


def append_new_rows_to_raw(
    env: str,
    batch_id: str,
    source_root: str = "data/generated",
    confirm_prod: bool = False,
) -> list[RawAppendResult]:
    from google.cloud import bigquery

    config = load_warehouse_config(env=env, confirm_prod=confirm_prod)
    client = get_bigquery_client(config)
    validation = validate_local_batch(batch_id=batch_id, source_root=source_root)

    validate_staging_load(
        env=env,
        batch_id=batch_id,
        source_root=source_root,
        confirm_prod=confirm_prod,
    )

    raw_dataset_ref = f"{config.project_id}.{config.raw_dataset}"
    client.create_dataset(bigquery.Dataset(raw_dataset_ref), exists_ok=True)

    results: list[RawAppendResult] = []
    for batch_file in validation.files:
        raw_table_id = f"{config.project_id}.{config.raw_dataset}.{batch_file.schema.table_name}"
        staging_table_id = (
            f"{config.project_id}.{config.staging_dataset}.{batch_file.schema.table_name}"
        )
        _ensure_raw_table(client, raw_table_id, batch_file.schema)

        rows_before = _count_rows(client, raw_table_id)
        _append_new_hashes(
            client=client,
            staging_table_id=staging_table_id,
            raw_table_id=raw_table_id,
            schema=batch_file.schema,
            source_file_name=batch_file.path.name,
        )
        rows_after = _count_rows(client, raw_table_id)
        results.append(
            RawAppendResult(
                table_name=batch_file.schema.table_name,
                rows_before=rows_before,
                rows_after=rows_after,
                inserted_rows=rows_after - rows_before,
            )
        )

    return results


def _ensure_raw_table(client, table_id: str, schema: ObjectSchema) -> None:
    from google.api_core.exceptions import NotFound
    from google.cloud import bigquery

    expected_schema = [
        *[bigquery.SchemaField(column, "STRING") for column in schema.columns],
        bigquery.SchemaField("row_hash", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("loaded_at", "TIMESTAMP", mode="REQUIRED"),
        bigquery.SchemaField("source_file_name", "STRING", mode="REQUIRED"),
    ]

    try:
        table = client.get_table(table_id)
    except NotFound:
        client.create_table(bigquery.Table(table_id, schema=expected_schema))
        return

    actual_columns = [field.name for field in table.schema]
    expected_columns = [field.name for field in expected_schema]
    missing_columns = [column for column in expected_columns if column not in actual_columns]
    if missing_columns:
        raise ValueError(f"Raw table {table_id} is missing columns: {missing_columns}")


def _append_new_hashes(
    client,
    staging_table_id: str,
    raw_table_id: str,
    schema: ObjectSchema,
    source_file_name: str,
) -> None:
    from google.cloud import bigquery

    source_columns = list(schema.columns)
    insert_columns = [*source_columns, *RAW_METADATA_COLUMNS]
    select_columns = ",\n  ".join(f"staged.`{column}`" for column in source_columns)
    hash_values = ", ".join(
        f"IFNULL(CAST(`{column}` AS STRING), '')" for column in source_columns
    )
    insert_column_sql = ", ".join(f"`{column}`" for column in insert_columns)

    sql = f"""
    INSERT INTO `{raw_table_id}` ({insert_column_sql})
    SELECT
      {select_columns},
      staged.row_hash,
      CURRENT_TIMESTAMP() AS loaded_at,
      @source_file_name AS source_file_name
    FROM (
      SELECT
        *,
        ROW_NUMBER() OVER (
          PARTITION BY row_hash
          ORDER BY `{schema.primary_key}`
        ) AS row_hash_rank
      FROM (
        SELECT
          *,
          TO_HEX(SHA256(TO_JSON_STRING([{hash_values}]))) AS row_hash
        FROM `{staging_table_id}`
      ) AS hashed
    ) AS staged
    WHERE staged.row_hash_rank = 1
      AND NOT EXISTS (
        SELECT 1
        FROM `{raw_table_id}` AS raw
        WHERE raw.row_hash = staged.row_hash
      )
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter(
                "source_file_name",
                "STRING",
                source_file_name,
            )
        ]
    )
    client.query(sql, job_config=job_config).result()


def _count_rows(client, table_id: str) -> int:
    rows = list(client.query(f"SELECT COUNT(*) FROM `{table_id}`").result())
    return int(rows[0][0])
