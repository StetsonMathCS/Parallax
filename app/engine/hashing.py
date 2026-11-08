import logging, hashlib, json, sys

GENESIS = hashlib.sha256("PARALLAX-ORIGIN".encode()).hexdigest()

logger = logging.getLogger(__name__)

def payload_hash(launch):
    """
    Computes a payload hash for a given launch record.
    """

    logger.info("Hashing payload for launch record: %s", launch.get("id"))

    payload = json.dumps(launch, sort_keys=True, separators=(',', ':')).encode()
    hashed_payload = hashlib.sha256(payload).hexdigest()

    logger.debug("Payload hash computed: %s", hashed_payload)

    return hashed_payload

def content_hash(launch):
    """
    Computes a content hash for the content of a given launch record.
    """

    logger.info("Hashing content for launch record: %s", launch.get("id"))

    content = {key: launch[key] for key in ("id", "name", "net", "window_start", "window_end", "status", "rocket", "mission")}
    hashed_content = payload_hash(content)

    logger.debug("Content hash computed: %s", hashed_content)

    return hashed_content

def chain_hash(launch, prev_hash, payload_hash, content_hash):
    """
    Computes a chain hash from the previous hash, payload, and content hashes.
    """

    logger.info("Hashing chain for launch record: %s", launch.get("id"))

    hashed_chain = hashlib.sha256("|".join((prev_hash, payload_hash, content_hash)).encode()).hexdigest()

    logger.debug("Chain hash computed: %s", hashed_chain)

    return hashed_chain

if __name__ == '__main__':
    """
    Computes payload and content hashes for a launch record.
    Usage:
        python hashing.py <path_to_launch_json>
    """

    logging.basicConfig(level=logging.DEBUG)

    with open(sys.argv[1]) as f: launch = json.load(f)

    payload = payload_hash(launch)
    logger.debug("Payload hash: %s", payload)

    content = content_hash(launch)
    logger.debug("Content hash: %s", content)

    chain = chain_hash(launch, GENESIS, payload, content)
    logger.debug("Chain hash: %s", chain)
