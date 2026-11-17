import logging, json

from pathlib import Path
from datetime import datetime

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

from engine import hashing
from helper import connect_to_db

def reader_connect():
    return connect_to_db.reader_user()

def payload_hash_verification():

    checked = 0
    mismatch = 0
    misses = []

    connection = reader_connect()
    logger.info("Connected to database as reader user")

    stored_records = connection.execute(
                """
                SELECT source_record_id, payload, payload_hash
                FROM raw.launch_records
                WHERE source_name = 'll2_prod'
                ORDER BY id DESC;
                """
            ).fetchall()
    try:
        for stored_record in stored_records:

            source_record_id, payload, payload_hash = stored_record

            logger.info("Checking launch ID: %s", source_record_id)

            logger.debug("Expected payload hash: %s", payload_hash)

            recomupted_hash = hashing.payload_hash(payload)

            logger.debug("Recomputed payload hash: %s", recomupted_hash)

            if recomupted_hash != payload_hash:
                logger.error("Launch ID %s has a hash mismatch", stored_record[0])
                logger.debug(payload)
                mismatch += 1

            checked += 1

    except Exception as e:
        logger.error("Error occurred while checking hashes: %s", str(e))

    logger.info("Final counts: %s Misses out of %s", mismatch, checked)
    logger.info(f"{misses}")


if __name__ == "__main__":

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    payload_hash_verification()
