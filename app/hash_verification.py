import logging

from pathlib import Path
from datetime import datetime

logging.basicConfig(level=logging.INFO)
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

    logger.info("Executing query to retrieve stored records")
    stored_records = connection.execute(
                """
                SELECT source_record_id, payload, payload_hash
                FROM raw.launch_records
                WHERE source_name = 'll2_prod'
                ORDER BY id ASC;
                """
            ).fetchall()

    logger.info("Retrieved %s stored records", len(stored_records))
    logger.info("Starting payload hash verification process")

    for stored_record in stored_records:
        try:
            source_record_id, payload, payload_hash = stored_record

            logger.debug("Checking launch ID: %s", source_record_id)

            logger.debug("Expected payload hash: %s", payload_hash)

            logger.debug("Recomputing payload hash")
            recomputed_hash = hashing.payload_hash(payload)

            logger.debug("Recomputed payload hash: %s", recomputed_hash)

            if recomputed_hash != payload_hash:
                logger.error("Launch ID %s has a hash mismatch", stored_record[0])
                logger.debug(payload)
                mismatch += 1
                misses.append(source_record_id)

            checked += 1

        except Exception as e:
            logger.error("Error occurred while checking hashes: %s", str(e))
            logger.debug(payload)
            mismatch += 1
            misses.append(source_record_id)

    logger.info("Final counts: %s Misses out of %s", mismatch, checked)

    if checked != len(stored_records) or mismatch != 0:
        if checked != len(stored_records):
            logger.error("Did not check %s records", len(stored_records) - checked)
            logger.error("Missing records: %s", [record[0] for record in stored_records[checked:]])
        if mismatch != 0:
            logger.info(f"{misses}")
            logger.error("Payload hash mismatch found in the above records")

    else:
        logger.info("All payloads passed")


def content_hash_verification():

    logger.info("Beginning content hash verification")

    checked = 0
    mismatch = 0
    misses = []

    connection = reader_connect()
    logger.info("Connected to database as reader user")

    logger.info("Executing query to retrieve stored records")
    stored_records = connection.execute(
                """
                SELECT source_record_id, payload, content_hash
                FROM raw.launch_records
                WHERE source_name = 'll2_prod'
                ORDER BY id ASC;
                """
            ).fetchall()

    logger.info("Retrieved %s stored records", len(stored_records))
    logger.info("Starting content hash verification process")

    for stored_record in stored_records:
        try:
            source_record_id, launch, content_hash = stored_record

            logger.debug("Checking launch ID: %s", source_record_id)

            logger.debug("Expected content hash: %s", content_hash)

            logger.debug("Recomputing content hash")
            recomputed_hash = hashing.content_hash(launch)

            logger.debug("Recomputed content hash: %s", recomputed_hash)

            if recomputed_hash != content_hash:
                logger.error("Launch ID %s has a hash mismatch", stored_record[0])
                logger.debug(launch)
                mismatch += 1
                misses.append(source_record_id)


            checked += 1

        except Exception as e:
            logger.error("Error occurred while checking hashes: %s", str(e))
            logger.debug(launch)
            mismatch += 1
            misses.append(source_record_id)

    logger.info("Final counts: %s Misses out of %s", mismatch, checked)

    if checked != len(stored_records) or mismatch != 0:
        if checked != len(stored_records):
            logger.error("Did not check %s records", len(stored_records) - checked)
            logger.error("Missing records: %s", [record[0] for record in stored_records[checked:]])
        if mismatch != 0:
            logger.info(f"{misses}")
            logger.error("Content hash mismatch found in the above records")

    else:
        logger.info("All content passed")

def chain_hash_verification():

    checked = 0
    mismatch = 0
    misses = []

    connection = reader_connect()
    logger.info("Connected to database as reader user")

    logger.info("Executing query to retrieve stored records")
    stored_records = connection.execute(
                """
                SELECT source_record_id, payload, payload_hash, content_hash, prev_hash, chain_hash
                FROM raw.launch_records
                WHERE source_name = 'll2_prod'
                ORDER BY id ASC;
                """
            ).fetchall()

    logger.info("Retrieved %s stored records", len(stored_records))
    logger.info("Starting chain hash verification process")

    for stored_record in stored_records:
        try:
            source_record_id, launch, payload_hash, content_hash, prev_hash, chain_hash = stored_record
            checked += 1

            if hashing.payload_hash(launch) != payload_hash:
                logger.error("Launch ID %s has a payload hash mismatch", stored_record[0])
                logger.debug(launch)
                mismatch += 1
                misses.append(source_record_id)
                continue

            if hashing.content_hash(launch) != content_hash:
                logger.error("Launch ID %s has a content hash mismatch", stored_record[0])
                logger.debug(launch)
                mismatch += 1
                misses.append(source_record_id)
                continue

            logger.debug("Checking launch ID: %s", source_record_id)

            logger.debug("Expected chain hash: %s", chain_hash)

            logger.debug("Recomputing chain hash")
            recomputed_hash = hashing.chain_hash(launch, prev_hash, payload_hash, content_hash)

            logger.debug("Recomputed chain hash: %s", recomputed_hash)

            if recomputed_hash != chain_hash:
                logger.error("Launch ID %s has a hash mismatch", stored_record[0])
                logger.debug(launch)
                mismatch += 1
                misses.append(source_record_id)

        except Exception as e:
            logger.error("Error occurred while checking hashes: %s", str(e))
            logger.debug(launch)
            mismatch += 1
            misses.append(source_record_id)

    logger.info("Final counts: %s Misses out of %s", mismatch, checked)

    if checked != len(stored_records) or mismatch != 0:
        if checked != len(stored_records):
            logger.error("Did not check %s records", len(stored_records) - checked)
            logger.error("Missing records: %s", [record[0] for record in stored_records[checked:]])
        if mismatch != 0:
            logger.info(f"{misses}")
            logger.error("Chain hash mismatch found in the above records")

    else:
        logger.info("All chains passed")


def previous_hash_verification():

    checked = 0
    mismatch = 0
    misses = []

    connection = reader_connect()
    logger.info("Connected to database as reader user")

    logger.info("Executing query to retrieve stored records")
    stored_records = connection.execute(
                """
                SELECT source_record_id, fetched_at, prev_hash, chain_hash
                FROM raw.launch_records
                WHERE source_name = 'll2_prod'
                ORDER BY id ASC;
                """
            ).fetchall()

    logger.info("Retrieved %s stored records", len(stored_records))
    logger.info("Starting previous hash verification process")

    previous_record_hash = {}

    for stored_record in stored_records:

        try:
            source_record_id, fetched_at, prev_hash, chain_hash = stored_record

            logger.debug("Checking launch ID: %s", source_record_id)

            logger.debug("Expected previous hash: %s", prev_hash)

            expected_previous_hash = previous_record_hash.get(source_record_id, hashing.GENESIS)

            logger.debug("Recomputed previous hash: %s", expected_previous_hash)

            if expected_previous_hash != prev_hash:
                logger.error("Launch ID %s has a hash mismatch", source_record_id)
                mismatch += 1
                misses.append(source_record_id)

            checked += 1

            previous_record_hash[source_record_id] = chain_hash

        except Exception as e:
            logger.exception("Error occurred while checking hashes: %s", str(e))
            logger.debug(source_record_id)
            mismatch += 1
            misses.append(source_record_id)

    logger.info("Previous hash counts: %s Misses out of %s", mismatch, checked)

    if checked != len(stored_records) or mismatch != 0:
        if checked != len(stored_records):
            logger.error("Did not check %s records", len(stored_records) - checked)
            logger.error("Missing records: %s", [record[0] for record in stored_records[checked:]])
        if mismatch != 0:
            logger.info(f"{misses}")
            logger.error("Hash mismatch for prev_hash found in the above records")

    else:
        logger.info("All previous hashes passed")


if __name__ == "__main__":

    payload_hash_verification()

    content_hash_verification()

    chain_hash_verification()

    previous_hash_verification()
