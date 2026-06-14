"""CLI wrapper for appending new hash-versioned rows into BigQuery raw tables."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from warehouse.merge_raw import append_new_rows_to_raw


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--env", choices=("test", "prod"), default="test")
    parser.add_argument("--batch-id", required=True)
    parser.add_argument("--source-root", default="data/generated")
    parser.add_argument("--confirm-prod", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    results = append_new_rows_to_raw(
        env=args.env,
        batch_id=args.batch_id,
        source_root=args.source_root,
        confirm_prod=args.confirm_prod,
    )
    print(f"Appended raw rows for batch {args.batch_id} in {args.env}:")
    for result in results:
        print(
            f"- {result.table_name}: inserted {result.inserted_rows} rows "
            f"({result.rows_before} -> {result.rows_after})"
        )


if __name__ == "__main__":
    main()

