import psycopg, logging, dotenv, os, json

from psycopg.types.json import Jsonb

from api import pull_data
from engine import hashing

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

logger.info("Started Data ingest")

dotenv.load_dotenv()

source_name, fetched_at, response_content, out = pull_data.ll2_api()

# Load the JSON data from the API response
launches = json.loads(response_content)["results"]
logger.info("Launches fetched: %d", len(launches))

# Database connection properties
connection = psycopg.connect(
    host=os.environ["DB_HOST"],
    port=os.environ["DB_PORT"],
    dbname=os.environ["POSTGRES_DB"],
    user=os.environ["INGEST_USER"],
    password=os.environ["INGEST_PASSWORD"],
)

logger.debug("Connected to database")

with connection:
    logger.info("Starting data insertion")

    inserted = 0
    skipped = 0

    for record, launch in enumerate(launches, start=1):

        logger.debug("Processing launch: %d", record)
        logger.debug("Launch ID: %s", launch["id"])

        # Get the previous chain hash for the launch record if it exists
        prev_hash = connection.execute(
            """
            SELECT chain_hash
            FROM raw.launch_records
            WHERE source_name = %s AND source_record_id = %s
            ORDER BY id DESC
            LIMIT 1;
            """,
            (source_name, launch["id"]),
        ).fetchone()

        prev_hash = prev_hash[0] if prev_hash else hashing.GENESIS

        if prev_hash:
            logger.debug("Previous hash for %s: %s", launch["id"], prev_hash)

        json_body = Jsonb(launch)
        payload_hash = hashing.payload_hash(launch)
        content_hash = hashing.content_hash(launch)
        chain_hash = hashing.chain_hash(launch, prev_hash, payload_hash, content_hash)

        # Insert the data into the database
        insertion_result = connection.execute(
            """
            INSERT INTO raw.launch_records
                (source_name, source_record_id, fetched_at, payload, payload_hash, content_hash, prev_hash, chain_hash)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING;
            """,
            (source_name, launch["id"], fetched_at, json_body, payload_hash, content_hash, prev_hash, chain_hash),
        )

        if insertion_result.rowcount:
            inserted += 1
            logger.debug("Inserted launch %s", launch["id"])
        else:
            skipped += 1
            logger.debug("Skipped launch %s", launch["id"])

    logger.info("Data written to database successfully: %d inserted, %d skipped", inserted, skipped)

connection.close()
