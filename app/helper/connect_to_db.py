import logging, psycopg, os, dotenv
import os

dotenv.load_dotenv()

logger = logging.getLogger(__name__)

def ingest_user():
    logger.info("Connecting to database")
    try:
        logger.info("Attempting to connect to database as ingest user")
        return psycopg.connect(
            host=os.environ["DB_HOST"],
            port=os.environ["DB_PORT"],
            dbname=os.environ["POSTGRES_DB"],
            user=os.environ["INGEST_USER"],
            password=os.environ["INGEST_PASSWORD"],
        )
    except:
        logger.error("Failed to connect to database")

def reader_user():
    logger.info("Connecting to database")
    try:
        logger.info("Attempting to connect to database as reader user")
        return psycopg.connect(
            host=os.environ["DB_HOST"],
            port=os.environ["DB_PORT"],
            dbname=os.environ["POSTGRES_DB"],
            user=os.environ["READER_USER"],
            password=os.environ["READER_PASSWORD"],
        )
    except:
        logger.error("Failed to connect to database")


def postgres_user():
    logger.info("Connecting to database")
    try:
        logger.info("Attempting to connect to database as postgres user")
        return psycopg.connect(
            host=os.environ["DB_HOST"],
            port=os.environ["DB_PORT"],
            dbname=os.environ["POSTGRES_DB"],
            user=os.environ["POSTGRES_USER"],
            password=os.environ["POSTGRES_PASSWORD"],
        )
    except:
        logger.error("Failed to connect to database")
