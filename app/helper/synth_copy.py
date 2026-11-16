import glob, os, json, logging, time

import datetime

from pathlib import Path
from engine import hashing

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Synth Directory

SYNTH_DIR = Path(__file__).parent / "data/synth_data"
SYNTH_DIR.mkdir(parents=True, exist_ok=True)

def load_most_recent_original(path):
    files = list(Path(path).glob("*.json"))
    most_recent = max(files, key=lambda file: datetime.datetime.fromtimestamp(file.stat().st_mtime))
    # with open(most_recent) as f:
    #    return json.load(f)
    return most_recent

def synth_pure_copy(path):
    logger.info("Begin synthetic copy process")
    pure_copy_dir = SYNTH_DIR / "pure_copy"
    pure_copy_dir.mkdir(parents=True, exist_ok=True)
    original_data = json.load(open(load_most_recent_original(path)))
    fetched_at = datetime.datetime.now(datetime.timezone.utc)
    output_file = pure_copy_dir / f"pure_copy_ll2_{fetched_at:%Y%m%dT%H%M%SZ}.json"
    with open(output_file, "w") as f:
        original = original_data["results"]
        for launch in original:
            launch["id"] = launch['id'] + '_synthetic_copy'
            json.dump(launch, f)
            f.write("\n")
        logger.info("Pure copy written to %s", output_file)
        return json.dumps(original_data["results"])

def synth_second_source(path):
    logger.info("Beginning creation of synthetic second source.")
    synth_src_dir = SYNTH_DIR / "synth_src"
    synth_src_dir.mkdir(parents=True, exist_ok=True)
    original_data = json.load(open(load_most_recent_original(path)))
    fetched_at = datetime.datetime.now(datetime.timezone.utc)
    output_file = synth_src_dir / f"synth_src_{fetched_at:%Y%m%dT%H%M%SZ}.json"
    with open(output_file, "w") as f:
        original = original_data["results"]
        for launch in original:
            launch["id"] = hashing.content_hash(launch) + '_second_src'
            json.dump(launch, f)
            f.write("\n")
        logger.info("Synthetic second source written to %s", output_file)
        return json.dumps(original_data["results"])
