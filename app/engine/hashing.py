import logging, hashlib, json, sys

def canonical_hash(launch):
    """
    Computes a canonical hash for a given launch record.
    """
    canon = json.dumps(launch, sort_keys=True, separators=(',', ':')).encode()
    logging.debug("Canonical representation of launch: %s", canon)
    return hashlib.sha256(canon).hexdigest()

def content_hash(launch):
    """
    Computes a canonical hash for the content of a given launch record.
    """
    content = {key: launch[key] for key in ("id", "name", "net", "window_start", "window_end", "status")}
    logging.debug("Content representation of launch: %s", content)
    return canonical_hash(content)

if __name__ == '__main__':

    logging.basicConfig(level=logging.DEBUG)

    launch = json.loads(sys.argv[1])

    canonical_hash(launch)

    content_hash(launch)
