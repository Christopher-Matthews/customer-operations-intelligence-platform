"""CLI wrapper for validating a BigQuery staging load."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from warehouse.validate_load import validate_staging_load


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--env", choices=("test", "prod"), default="test")
    parser.add_argument("--batch-id", required=True)
    parser.add_argument("--source-root", default="data/generated")
    parser.add_argument("--confirm-prod", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    results = validate_staging_load(
        env=args.env,
        batch_id=args.batch_id,
        source_root=args.source_root,
        confirm_prod=args.confirm_prod,
    )
    print(f"Validated staging batch {args.batch_id} in {args.env}:")
    for result in results:
        print(
            f"- {result.table_name}: {result.staging_rows} staging rows, "
            f"{result.local_rows} local rows, "
            f"{result.duplicate_primary_keys} duplicate keys, "
            f"{result.blank_primary_keys} blank keys"
        )


if __name__ == "__main__":
    main()

