# Parallax - Spaceflight Tracking and Data Verification

A spaceflight and launch-tracking system that combines multi-source verification, tamper-evident logging, and confidence scoring to provide a trustworthy, provenance view of launch and satellite telemetry data.

## Abstract

Existing launch and spaceflight tracking applications ingest data through a variety of sources from governmental to private entities. This data, ingested and shared amongst each other, has no verifiable way to safeguard against data malformation originating from a corrupt input or data manipulated with malicious intent, potentially leading to a cascading data poisoning due to shared information. Our application seeks to resolve this by evaluating each piece of data against multiple data sources without assuming independence, creating a weighted confidence score. Tamper-evident logging as demonstrated by Crosby and Wallach 2009, protects the integrity of each record and what each source asserted. With the potential for multiple adversaries, it is possible that satellite data can be compromised before data is even logged as discussed by Tedeschi, Sciancalepore, and Pietro 2022. Our verification system should be able to distinguish from information that is inaccurate instead of merely just stale. This, in no way, indicates an ability to identify a compromised satellite based on ingested information.  By purposefully injecting malformed data, we will be able to measure detection rate and false positives through the confidence scoring mechanism allowing us to challenge the system in such a way to keep the system as a whole accurate and honest. As the goal is to provide accurate data, provenance is an important aspect of every data source. By logging what data came from where and when, we can establish our own provenance of a source over time, therefore weighting sources differently enhancing our confidence scoring system in a method described by Pan, Stakhanova, and Ray 2023, to describe the history and evolution of a data object. The goal is to provide a verified view that has been cross-checked and references other sources with a quantifiable confidence indicator.

## Framework Outline

### Metrics

Caculate degree from origin based on update patterns, similiarity of mistakes, and observed origin
Confidence scoring should be based on observed and calculated degree from origin, number of sources in agreement, provenance of each source, 

### Pseudo Code

Include source of data with each datum

Variables:
- Observed_Degree_From_Origin
- Calculated_Degree_From_Origin
- Data_Source
- Timestamp
- audit_hash
- Confidence_Score
- Provenance_Info
- 

### Architecture

PostgreSQL Database, Redis Cache, Flask API, Dockerized Deployment. The system will ingest data from multiple sources, caluclate predefined metrics, and store the data in a PostgreSQL database. The system will also provide an API for querying the data and retrieving the confidence score and provenance information for each datum.

PostgreSQL Database:

The database will contain a table per data source, a table containing the audit log, caculated metrics, confidence scores, and provenance information.