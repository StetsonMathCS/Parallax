import psycopg, logging, dotenv, os, json, hashlib

from psycopg.types.json import Jsonb

from api import pull_data

logging.basicConfig(level=logging.DEBUG)
logging.info("Started Data ingest")

dotenv.load_dotenv()

def canonical_hash(launch):
    """
    Computes a canonical hash for a given launch record.
    """
    canon = json.dumps(launch, sort_keys=True, separators=(',', ':')).encode()
    return hashlib.sha256(canon).hexdigest()

source_name, fetched_at, response_content, out = pull_data.ll2_api()

# Load the JSON data from the API response
launches = json.loads(response_content)["results"]
logging.info("Launches fetched: %d", len(launches))

# Database connection properties
connection = psycopg.connect(
    host=os.environ["DB_HOST"],
    port=os.environ["DB_PORT"],
    dbname=os.environ["POSTGRES_DB"],
    user=os.environ["INGEST_USER"],
    password=os.environ["INGEST_PASSWORD"],
)

logging.debug("Connected to database")

with connection:
    logging.info("Starting data insertion")

    for record, launch in enumerate(launches, start=1):

        logging.debug("Processing launch: %d", record)

        # Insert the data into the database
        connection.execute(
            """
            INSERT INTO raw.launch_records
                (source_name, source_record_id, fetched_at, payload, payload_hash)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING;
            """,
            (source_name, launch["id"], fetched_at, Jsonb(launch), canonical_hash(launch)),
        )

    logging.info("Data written to database successfully")

connection.close()
