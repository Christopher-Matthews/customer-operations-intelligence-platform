"""CLI wrapper for loading a generated CSV batch into BigQuery staging."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from warehouse.load_staging import load_batch_to_staging


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--env", choices=("test", "prod"), default="test")
    parser.add_argument("--batch-id", required=True)
    parser.add_argument("--source-root", default="data/generated")
    parser.add_argument("--confirm-prod", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    results = load_batch_to_staging(
        env=args.env,
        batch_id=args.batch_id,
        source_root=args.source_root,
        confirm_prod=args.confirm_prod,
    )
    print(f"Loaded staging batch {args.batch_id} into {args.env}:")
    for result in results:
        print(
            f"- {result.table_name}: {result.loaded_rows} rows "
            f"from {result.file_name} ({result.local_rows} local)"
        )


if __name__ == "__main__":
    main()

