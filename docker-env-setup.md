Create .env file

Copy the existing .env.example and using openssl generate random passwords. The .env will be used by docker-compose to set the environment variables.

```bash
cat >> .env <<EOF
POSTGRES_USER=parallax
POSTGRES_PASSWORD=$(openssl rand -hex 24)
POSTGRES_DB=parallax_db
EOF
```

You can copy the .env.example to provide custom values.

## Database Commands

**1. Open a `psql` session as the admin user:**
```bash
docker compose exec parallax-db psql -U parallax -d parallax_db
```

**2. Inside `psql`, create the role, password, and create the database:**
```sql
CREATE ROLE n8n WITH LOGIN;
\password n8n
CREATE DATABASE n8n OWNER n8n;
REVOKE CONNECT ON DATABASE n8n FROM PUBLIC;
```

**3. Verify:**
```sql
\l
\du
\q # quits
```

**4. Test the new login works.**

Test using localhost wih password:
```bash
docker compose exec parallax-db psql -U n8n -d n8n -h 127.0.0.1 -c '\conninfo'
```

## New Roles

```bash
cat >> .env <<EOF
INGEST_USER=ingest
INGEST_PASSWORD=$(openssl rand -hex 24)
READER_USER=reader
READER_PASSWORD=$(openssl rand -hex 24)
METRIC_USER=metric
METRIC_PASSWORD=$(openssl rand -hex 24)
EOF
```

**Permissions:**

| Role | `raw` schema | `metrics` schema |
|---|---|---|
| `ingest` | INSERT, SELECT | none |
| `metric` | SELECT | owns it, so full control |
| `reader` | SELECT | SELECT |


**Inserting sql using `roles.sql` as the admin user:**

```sql
-- Create the roles (ingest already exists)
-- CREATE ROLE ingest LOGIN;
CREATE ROLE reader LOGIN;
CREATE ROLE metric LOGIN;

-- Least privilege
ALTER ROLE ingest NOSUPERUSER NOCREATEDB NOCREATEROLE;
ALTER ROLE reader NOSUPERUSER NOCREATEDB NOCREATEROLE;
ALTER ROLE metric NOSUPERUSER NOCREATEDB NOCREATEROLE;

-- Only these roles can connect
REVOKE CONNECT ON DATABASE parallax_db FROM PUBLIC;
GRANT CONNECT ON DATABASE parallax_db TO ingest, reader, metric;

-- raw table created by the admin, written by ingest
CREATE SCHEMA raw;
GRANT USAGE ON SCHEMA raw TO ingest, reader, metric;
GRANT INSERT, SELECT ON ALL TABLES IN SCHEMA raw TO ingest;
GRANT SELECT ON ALL TABLES IN SCHEMA raw TO reader, metric;
ALTER DEFAULT PRIVILEGES IN SCHEMA raw GRANT INSERT, SELECT ON TABLES TO ingest;
ALTER DEFAULT PRIVILEGES IN SCHEMA raw GRANT SELECT ON TABLES TO reader, metric;
ALTER DEFAULT PRIVILEGES IN SCHEMA raw GRANT USAGE ON SEQUENCES TO ingest;

-- metrics owned and written only by metric
CREATE SCHEMA metrics AUTHORIZATION metric;
GRANT USAGE ON SCHEMA metrics TO reader;
ALTER DEFAULT PRIVILEGES FOR ROLE metric IN SCHEMA metrics GRANT SELECT ON TABLES TO reader;
```

Run it from the Parallax folder:
```bash
docker compose exec -T parallax-db psql -U parallax -d parallax_db -v ON_ERROR_STOP=1 < roles.sql
```

**Set the passwords after:**
```bash
docker compose exec -it parallax-db psql -U parallax -d parallax_db
```

```psql
\password reader # Done
\password metric # Done
\password ingest # Already done
\q
```

## Raw record Schema

```sql
docker compose exec -T parallax-db psql -U parallax -d parallax_db -v ON_ERROR_STOP=1 < schema.sql
```

## Role verification

```sql
docker compose exec parallax-db psql
 -U ingest -d parallax_db -h 127.0.0.1
psql (18.6 (Debian 18.6-1.pgdg13+2))
Type "help" for help.

parallax_db=> INSERT INTO raw.launch_record (source_name, source_record_id, fetched_at, payload, payload_hash)
VALUES ('test', 'x1', now(), '{}', repeat('a', 64));
INSERT 0 1
parallax_db=> SELECT id, source_name FROM raw.launch_record;
 id | source_name
----+-------------
  1 | test
(1 row)

parallax_db=> UPDATE raw.launch_record SET source_name = 'intentionally_modified' WHERE id = 1;
ERROR:  permission denied for table launch_record
parallax_db=> DELETE FROM raw.launch_record WHERE id = 1;
ERROR:  permission denied for table launch_record
parallax_db=> \q
```

## DB Record Verification

Logging output showing successful writes to DB and skipped content due to no change.

`docker compose exec parallax-db psql -U parallax -d parallax_db -c "SELECT source_name, count(*) FROM raw.launch_records GROUP BY 1;"`

 source_name | count
-------------+-------
 ll2         |   100
(1 row)

```bash
DEBUG:__main__:Processing launch: 10
DEBUG:__main__:Launch ID: e7a1e5ba-62fd-4f4d-9343-fa2cc0141904
DEBUG:__main__:Previous hash for e7a1e5ba-62fd-4f4d-9343-fa2cc0141904: 8e98cdaee00d1f169131269a69bc64fafb8b58a298878a4f0b84e4d94eef8ee4
INFO:engine.hashing:Hashing payload for launch record: e7a1e5ba-62fd-4f4d-9343-fa2cc0141904
DEBUG:engine.hashing:Payload hash computed: 51c9ed6718bad6f504b258deeffe3021d9bfb5e08849ea9298491e1a8235e4c9
INFO:engine.hashing:Hashing content for launch record: e7a1e5ba-62fd-4f4d-9343-fa2cc0141904
INFO:engine.hashing:Hashing payload for launch record: e7a1e5ba-62fd-4f4d-9343-fa2cc0141904
DEBUG:engine.hashing:Payload hash computed: cf9ee20e67b5592921e479cf777322fe024510a129c0b2d8778f0f1a0c517d9f
DEBUG:engine.hashing:Content hash computed: cf9ee20e67b5592921e479cf777322fe024510a129c0b2d8778f0f1a0c517d9f
INFO:engine.hashing:Hashing chain for launch record: e7a1e5ba-62fd-4f4d-9343-fa2cc0141904
DEBUG:engine.hashing:Chain hash computed: 1f16910aaa0eed3b2f21331cbdc28df585c5a2456390248c60e01911ae553dd0
DEBUG:__main__:Skipped launch e7a1e5ba-62fd-4f4d-9343-fa2cc0141904
INFO:__main__:Data written to database successfully: 0 inserted, 10 skipped
```
