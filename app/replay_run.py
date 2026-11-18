import logging, re, json

from datetime import datetime, timezone

from pathlib import Path

logger = logging.getLogger(__name__)

import write_to_db

DATA_DIR = Path("api/data")

# Regex matching 8 digits, literal 'T', 6 digits, and literal 'Z'
TIMESTAMP_PATTERN = re.compile(r"(\d{8}T\d{6}Z)")

def replay_prod():
    data_dir = DATA_DIR / "ll2prod"

    files = [f.name for f in data_dir.iterdir() if f.is_file()]

    payloads = []

    for file in files:
        match = TIMESTAMP_PATTERN.search(file)
        if match:
            fetched_at = datetime.strptime(match.group(1), "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc)
            payloads.append((fetched_at, file))

    payloads.sort()

    for fetched_at, file in payloads:
        launches = json.load(open(data_dir / file))["results"]
        write_to_db.write_to_db(launches,"ll2_prod", fetched_at)
        logger.info(f"Replayed {file} with fetched_at {fetched_at}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    replay_prod()
