# Parallax - Spaceflight Tracking and Data Verification

A launch-tracking system that combines source provenance, and content hashing, to deliver a view of what a source said and when.

## Abstract

Data ingestion through API is a common practice and generally thought of as secure due to the intentional nature of the request. What do we do then when we have little variation in data sources? Existing launch and spaceflight applications have little variation in data source and they often share data. This data has no verifiable way to safeguard against data malformation originating from a corrupt input or data manipulated with malicious intent, potentially leading to a cascading data poisoning due to shared information. By applying content hashing, source provenance tracking, and copy detection, we are able to describe what a source said, when they said and and what was copied.

---

## Framework Outline

### Pseudo Code

Ingestion:
- Get data from source - pull_data.py
- Include source of data with each datum - pull_data.py
- hash results and content - hashing.py
- Check for existing IDs - write_to_db
- previous hash is genesis where no record exists - write_to_db, GENESIS in hashing
- Chain hash becomes hash of payload, content and previous - hashing
- Write results to DB - write_to_db
- Unchanged content skipped - Handled by DB, logged in write_to_db

Metrics:



### Architecture

PostgreSQL Database, Dockerized Deployment. The system will ingest data from multiple sources, calculate predefined metrics, and store the data in a PostgreSQL database.

PostgreSQL Database:

The database will contain a table per data source, a table containing the audit log, caculated metrics, confidence scores, and provenance information.
