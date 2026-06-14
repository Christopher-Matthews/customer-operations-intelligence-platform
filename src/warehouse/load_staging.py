"""Load generated CSV batches into BigQuery staging tables."""

from __future__ import annotations

from dataclasses import dataclass

from warehouse.config import get_bigquery_client, load_warehouse_config
from warehouse.schemas import BatchFile, validate_local_batch


@dataclass(frozen=True)
class StagingLoadResult:
    table_name: str
    file_name: str
    local_rows: int
    loaded_rows: int | None


def load_batch_to_staging(
    env: str,
    batch_id: str,
    source_root: str = "data/generated",
    confirm_prod: bool = False,
) -> list[StagingLoadResult]:
    from google.cloud import bigquery

    config = load_warehouse_config(env=env, confirm_prod=confirm_prod)
    client = get_bigquery_client(config)
    validation = validate_local_batch(batch_id=batch_id, source_root=source_root)

    dataset_ref = f"{config.project_id}.{config.staging_dataset}"
    client.create_dataset(bigquery.Dataset(dataset_ref), exists_ok=True)

    results: list[StagingLoadResult] = []
    for batch_file in validation.files:
        table_id = f"{config.project_id}.{config.staging_dataset}.{batch_file.schema.table_name}"
        job_config = bigquery.LoadJobConfig(
            source_format=bigquery.SourceFormat.CSV,
            skip_leading_rows=1,
            schema=[bigquery.SchemaField(column, "STRING") for column in batch_file.schema.columns],
            write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
            autodetect=False,
        )
        with batch_file.path.open("rb") as csv_file:
            load_job = client.load_table_from_file(
                csv_file,
                table_id,
                job_config=job_config,
            )
        load_job.result()
        destination_table = client.get_table(table_id)
        results.append(
            StagingLoadResult(
                table_name=batch_file.schema.table_name,
                file_name=batch_file.path.name,
                local_rows=batch_file.row_count,
                loaded_rows=destination_table.num_rows,
            )
        )

    return results


def detected_batch_files(batch_id: str, source_root: str = "data/generated") -> tuple[BatchFile, ...]:
    return validate_local_batch(batch_id=batch_id, source_root=source_root).files

