import logging , requests
import hashlib
import re
import json
from pathlib import Path
import time
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

def dir_setup():
    # Path to saved data files
    try:

        DATA_DIR = Path(__file__).parent / "data"
        DATA_DIR.mkdir(exist_ok=True)
        logger.info("Data directory ready: %s", DATA_DIR)

        PAGES_DIR = DATA_DIR / "ll2_backfill"
        PAGES_DIR.mkdir(exist_ok=True)
        logger.info("Pages directory ready: %s", PAGES_DIR)

        NEXT_URL = PAGES_DIR / "next_url.txt"
        logger.info("Next URL file ready: %s", NEXT_URL)
        return DATA_DIR, PAGES_DIR, NEXT_URL

    except OSError as e:

        logger.error("Failed to create directory: %s", e)
        raise

# Parameters for the API request
ll2_params = {
    "limit": 100,
    "ordering": "net"
}

# API URL for the SpaceDevs Launch Library 2
api_url = "https://ll.thespacedevs.com/2.3.0/launches/"

def _throttle_wait(resp):
    if "Retry-After" in resp.headers:
        return int(resp.headers["Retry-After"]) + 1
    m = re.search(r"(\d+)\s+seconds", resp.text, re.IGNORECASE)
    if m:
        return int(m.group(1)) + 1
    return 300

def backfill(PAGES_DIR, NEXT_URL):

    logger.info("Starting backfill process")

    existing_pages = list(PAGES_DIR.glob("page_*.json"))

    if existing_pages and not NEXT_URL.exists():
        logger.info("Backfill already completed")
        return

    url = NEXT_URL.read_text().strip() if NEXT_URL.exists() else api_url
    params = None if NEXT_URL.exists() else ll2_params
    page_no = len(existing_pages) + 1

    logger.info("Initial URL: %s", url)
    logger.info("Initial params: %s", ll2_params)

    while url:

        logger.info("Fetching URL: %s", url)

        resp = requests.get(url, params=params, timeout=30)
        params = None
        logger.info("Response status code: %d", resp.status_code)

        if resp.status_code == 200:
            # Process the data as needed
            logger.info("Successfully fetched data from URL: %s", url)
            params = None
            fetched_at = datetime.now(timezone.utc)
            page = PAGES_DIR / f"page_{page_no:03d}.json"
            page.write_bytes(resp.content)
            logger.info("Saved page to %s", page)
            logger.info("%s sha256=%s fetched=%s", page, hashlib.sha256(resp.content).hexdigest()[:16], fetched_at.isoformat())

            url = resp.json().get("next")
            if url:
                NEXT_URL.write_text(url)
            else:
                NEXT_URL.unlink(missing_ok=True)
            page_no += 1

        elif resp.status_code == 429:
            wait_time = _throttle_wait(resp)
            logger.warning("Throttled. Retrying in %d seconds", wait_time)
            time.sleep(wait_time)
            continue

        else:
            logger.error("Failed to fetch data from URL: %s. Status code: %d", url, resp.status_code)
            resp.raise_for_status()
            break

def merge_pages(DATA_DIR, PAGES_DIR):
    records, count = {}, 0

    for p in sorted(PAGES_DIR.glob("page_*.json")):
        payload = json.loads(p.read_bytes())
        count = payload["count"]
        for record in payload["results"]:
            records[record["id"]] = record

    if len(records) != count:
        logger.warning("Record count mismatch: expected %d, got %d", count, len(records))

    out = DATA_DIR / f"ll2_full_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.json"
    out.write_text(json.dumps({"count": count, "results": list(records.values())}))
    logger.info("Wrote %d records to %s", len(records), out)
    return out

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    DATA_DIR, PAGES_DIR, NEXT_URL = dir_setup()
    backfill(PAGES_DIR, NEXT_URL)
    merge_pages(DATA_DIR, PAGES_DIR)
