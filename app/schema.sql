CREATE TABLE raw.launch_records (
    id               BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    source_name      TEXT        NOT NULL,
    source_record_id TEXT        NOT NULL,
    fetched_at       TIMESTAMPTZ  NOT NULL,
    payload          JSONB       NOT NULL,
    payload_hash     CHAR(64)    NOT NULL,
    content_hash     CHAR(64)   NOT NULL,
    prev_hash         CHAR(64),
    chain_hash      CHAR(64),
    UNIQUE (source_name, source_record_id, content_hash)
);
