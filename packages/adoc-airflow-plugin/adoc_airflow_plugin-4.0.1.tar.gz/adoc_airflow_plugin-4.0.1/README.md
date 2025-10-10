## Overview
The Acceldata Listener plugin integrates Airflow DAGs for automatic observation in ADOC.

## Features
The plugin performs the following actions without requiring additional code in your Airflow DAG, unless you disable instrumentation through environment variables.

- **When the DAG starts:**
  - It creates the pipeline if it does not already exist in ADOC.
  - It creates a new pipeline run in ADOC.

- **When a TaskInstance starts:**
  - It creates jobs in ADOC for each of the Airflow operators used in the task.
  - It constructs job input nodes based on the upstream tasks.
  - It creates a span and associates it with the jobs.
  - It emits span events with metadata.

- **When a TaskInstance is completed:**
  - It emits span events with metadata.
  - It ends the spans with either success or failure.

- **When the DAG is completed:**
  - It updates the pipeline run with success or failure in ADOC.

## Prerequisites
Ensure the following applications are installed on your system:
- Python V3.8.0 and above ([Download Python](https://www.python.org/downloads/))
- Airflow V2.5.0 and above ([Apache Airflow](https://airflow.apache.org/docs/apache-airflow/stable/installation.html))

API keys are essential for authentication when making calls to ADOC. You can generate API keys in the ADOC UI's Admin Central by visiting the [API Keys](https://docs.acceldata.io/documentation/api-keys) section.

## Configuration

### Plugin Environment Variables
The `adoc_airflow_plugin` uses the `acceldata-sdk` to push data to the ADOC backend.

**Mandatory Environment Variables:**
The ADOC client requires the following environment variables:
- `TORCH_CATALOG_URL`: The URL of your ADOC Server instance.
- `TORCH_ACCESS_KEY`: The API access key generated from the ADOC UI.
- `TORCH_SECRET_KEY`: The API secret key generated from the ADOC UI.

**Optional Environment Variables:**
By default, all DAGs are observed. However, the following environment variables can be set to modify this behavior.

**Note:** The variables for ignoring or observing DAGs are mutually exclusive.

- If the following environment variables match specific DAG IDs, those DAGs will be ignored from observation, while all other DAGs will still be observed:
  - `DAGIDS_TO_IGNORE`: Comma-separated list of DAG IDs to ignore.
  - `DAGIDS_REGEX_TO_IGNORE`: Regular expression pattern for DAG IDs to ignore.

- If the following environment variables match specific DAG IDs, only those DAGs will be observed, and all others will be ignored:
  - `DAGIDS_TO_OBSERVE`: Comma-separated list of DAG IDs to observe.
  - `DAGIDS_REGEX_TO_OBSERVE`: Regular expression pattern for DAG IDs to observe.
