CREATE TABLE raw.launch_records (
    id               BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    source_name      TEXT        NOT NULL,
    source_record_id TEXT        NOT NULL,
    fetched_at       TIMESTAMPTZ  NOT NULL,
    payload          JSONB       NOT NULL,
    payload_hash     CHAR(64)    NOT NULL,
    prev_hash         CHAR(64),
    UNIQUE (source_name, source_record_id, payload_hash)
);
