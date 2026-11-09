import logging , requests
from pathlib import Path
from datetime import datetime, timezone

# Path to saved data files
DATA_DIR = Path(__file__).parent / "data"

logger = logging.getLogger(__name__)

# Parameters for the API request
ll2_params = {
    "limit": 100,
    "ordering": "last_updated"
}

# API URL for the SpaceDevs Launch Library 2
api_url = "https://ll.thespacedevs.com/2.3.0/launches/"


def ll2_api():
    """
    Fetches data from the SpaceDevs Launch Library 2 API and saves it to a file.
    Returns:
        source_name (str): The name of the data source.
        fetched_at (datetime): The timestamp when the data was fetched.
        response.content (bytes): The raw content of the API response.
        out (Path): The path to the saved file.
    Raises:
        requests.RequestException: If the API request fails.
        Exception: For any other exceptions that may occur.
    """
    try:

        logger.info("Trying first Source: %s", api_url)

        # Save request
        response = requests.get(api_url, params=ll2_params, timeout=10)

        # Fetched timestamp in UTC
        fetched_at = datetime.now(timezone.utc)

        # Raise on HTTP errors
        response.raise_for_status()

        logger.info("Status: %s", response.status_code)

        # Creates directory if it doesn't exist and save the response
        DATA_DIR.mkdir(exist_ok=True)
        out = DATA_DIR / f"ll2_{fetched_at:%Y%m%dT%H%M%SZ}.json"
        out.write_bytes(response.content)

        logger.info("Wrote to file")

        return "ll2", fetched_at, response.content, out

    except requests.RequestException as requestException:
        logger.error("LL2 fetch failed: %s", requestException)
        raise

    except Exception as e:
        logger.error("LL2 fetch failed: %s", e)
        raise

if __name__ == '__main__':

    logging.basicConfig(level=logging.DEBUG)

    ll2_api()
