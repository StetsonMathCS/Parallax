import logging
import json
import sys

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from helper import connect_to_db
import hash_verification

def connect_as_admin():
    connection = connect_to_db.postgres_user()
    return connection

def launch_records_backup():
    logger.info("Backing up launch records table")

    connection = connect_as_admin()

    original_count = connection.execute("SELECT COUNT(*) FROM raw.launch_records;").fetchone()[0]

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS raw.launch_records_backup AS
        SELECT * FROM raw.launch_records;
        """
        )

    connection.commit()

    backup_count = connection.execute("SELECT COUNT(*) FROM raw.launch_records_backup;").fetchone()[0]

    if backup_count == original_count:
        logger.info("Backed up %s records", original_count)

    else:
        logger.error("Failed to backup all records: %s Backed up, %s Original", backup_count, original_count)

        logger.error("Running record verification")

        try:
            verify_hash_records()
            logger.error("Recreating backup table")
            connection.execute(
            """
            DROP TABLE IF EXISTS raw.launch_records_backup;
            """
            )
            connection.commit()
            launch_records_backup()

        except Exception as e:
            logger.exception("Failed to verify hash records: %s", str(e))
            sys.exit(1)


def restore_removed_record(record_id):
    connection = connect_as_admin()

    connection.execute(
        """
        INSERT INTO raw.launch_records
        OVERRIDING SYSTEM VALUE
        SELECT * FROM raw.launch_records_backup WHERE id = %s;
        """
    , (record_id,))

    connection.commit()

    logger.info("Restored record %s", record_id)

def remove_record():
    connection = connect_as_admin()

    selected_launch = connection.execute(
        """
        SELECT source_name, source_record_id, count(*)
        FROM raw.launch_records
        GROUP BY 1, 2
        HAVING count(*) > 1
        ORDER BY 3 DESC;
        """
        ).fetchone()

    launch_rows = connection.execute(
    """
    SELECT id
    FROM raw.launch_records
    WHERE source_record_id = %s
    ORDER BY id ASC;
    """
    , (selected_launch[1],)).fetchall()

    connection.execute(
        """
        DELETE FROM raw.launch_records
        WHERE id = %s;
        """
    , (launch_rows[1][0],))

    connection.commit()

    logger.info("Removed record %s", selected_launch[1])

    return launch_rows[1][0], selected_launch[1]

def restore_tampered_record(record_id):
    connection = connect_as_admin()

    connection.execute(
        """
        UPDATE raw.launch_records tampered
        SET payload = backup.payload
        FROM raw.launch_records_backup backup
        WHERE tampered.id = backup.id and tampered.id = %s;
        """
    , (record_id,))

    connection.commit()

    logger.info("Restored record %s", record_id)

def tamper_record(test_record_id):

    connection = connect_as_admin()

    logger.info("Connected to database")

    payload = connection.execute(
        """
        SELECT payload
        FROM raw.launch_records
        WHERE id = %s;
        """
    , (test_record_id,)).fetchone()

    logger.debug(payload[0]["id"])

    payload[0]["id"] = 'tampered_launch_record'

    logger.debug(payload[0]["id"])

    connection.execute(
        """
        UPDATE raw.launch_records
        SET payload = %s
        WHERE id = %s;
        """
    , (json.dumps(payload[0]), test_record_id))

    connection.commit()

    logger.info("Tampered with record %s", test_record_id)

def verify_hash_records():
    hash_verification.payload_hash_verification()

    hash_verification.content_hash_verification()

    hash_verification.chain_hash_verification()

    hash_verification.previous_hash_verification()

if __name__ == "__main__":

    verify_hash_records()

    launch_records_backup()

    try:
        removed_launch_id, test_record_id = remove_record()
        verify_hash_records()

    finally:
        restore_removed_record(removed_launch_id)
        verify_hash_records()


    try:
        debug_test_record_id = 9946
        logger.debug("Debug test record ID: %s", debug_test_record_id)
        tamper_record(debug_test_record_id)
        verify_hash_records()

    finally:
        restore_tampered_record(debug_test_record_id)
        verify_hash_records()
