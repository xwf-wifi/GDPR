"""Extract a reproducible top-100 sample from the committed Tranco archive."""

import argparse
import csv
import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path

ARCHIVE = Path(__file__).with_name("tranco_64X3X-1m.csv.zip")


def extract(archive: Path, count: int = 100) -> list[dict]:
    with zipfile.ZipFile(archive) as zipped:
        names = zipped.namelist()
        if len(names) != 1:
            raise ValueError("Expected exactly one CSV in the Tranco archive")
        with zipped.open(names[0]) as source:
            # CSV fields here are ASCII-compatible; decoding line by line keeps memory small.
            rows = csv.reader((line.decode("utf-8-sig") for line in source))
            sites = []
            for expected_rank in range(1, count + 1):
                row = next(rows, None)
                if row is None or len(row) != 2 or int(row[0]) != expected_rank:
                    raise ValueError(f"Missing or unexpected Tranco rank {expected_rank}: {row}")
                sites.append({"rank": expected_rank, "domain": row[1].strip().lower()})
    return sites


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, default=ARCHIVE)
    parser.add_argument("--count", type=int, default=100)
    parser.add_argument("--output", type=Path, default=Path("data/top100.json"))
    args = parser.parse_args()
    if args.count < 1:
        parser.error("--count must be positive")
    payload = {
        "source": "Tranco",
        "list_id": "64X3X" if args.archive.resolve() == ARCHIVE.resolve() else None,
        "archive": args.archive.name,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "sites": extract(args.archive, args.count),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(payload['sites'])} sites to {args.output}")


if __name__ == "__main__":
    main()
