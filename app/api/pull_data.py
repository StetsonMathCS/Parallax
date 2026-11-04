import logging , requests
from pathlib import Path
from datetime import datetime, timezone

DATA_DIR = Path(__file__).parent / "data"


def ll2_api():

    ll_params = {
    "limit": 10,
    "ordering": "last_updated"
}
        
    try:
        api_url = "https://ll.thespacedevs.com/2.3.0/launches/"

        logging.info("Trying first Source: %s", api_url)

        response = requests.get(api_url, params=ll_params, timeout=10)

        fetched_at = datetime.now(timezone.utc)

        if response.status_code == 200:
            logging.info("Status: %s", response.status_code)

            DATA_DIR.mkdir(exist_ok=True)
            out = DATA_DIR / f"ll2_{fetched_at:%Y%m%dT%H%M%SZ}.json"
            out.write_bytes(response.content)

            logging.info("Wrote to file")

        else:
            logging.info("Status: %s", response.status_code)

        return fetched_at, out

    except Exception as e:
        logging.error(e)

if __name__ == '__main__':

    logging.basicConfig(level=logging.DEBUG)

    ll2_api()

    
        



