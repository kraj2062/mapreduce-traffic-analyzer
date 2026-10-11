# mapreduce-traffic-analyzer

A cloud-deployed REST API that analyzes synthetic traffic records and
summarizes congestion patterns by location. The project uses a
**MapReduce-style batch-processing pipeline** implemented with Python,
FastAPI, and SQLite.

**Deployment:** Live on Render. The `/health` endpoint returned HTTP 200
during verification.

## Links

-   [Live service](https://mapreduce-traffic-analyzer.onrender.com)
-   [Health
    check](https://mapreduce-traffic-analyzer.onrender.com/health)
-   [Interactive API
    documentation](https://mapreduce-traffic-analyzer.onrender.com/docs)
-   [GitHub
    repository](https://github.com/kraj2062/mapreduce-traffic-analyzer)

## Features

-   Six REST endpoints for health, traffic upload, analysis, results,
    location summaries, and metrics.
-   API-key protection on protected endpoints through the `X-API-Key`
    header.
-   Input validation for traffic records.
-   Map → Shuffle/Group → Reduce-style batch processing.
-   SQLite storage for raw records and analysis results.
-   Application logging and a basic metrics endpoint.
-   Dataset-size benchmarks and API load-test evidence.
-   Invalid-input validation test and subsequent health check.

## Architecture

See `MapReduce_Traffic_Analyzer_Architecture.png`. Requests from a
browser/Swagger UI or HTTP client reach the FastAPI service hosted on
Render. The API validates and routes requests to the processing pipeline
and SQLite data layer.

## REST endpoints

  Method   Endpoint                Purpose
  -------- ----------------------- ------------------------------------
  GET      `/health`               Service health check
  POST     `/traffic/upload`       Validate and store traffic records
  POST     `/analysis/run`         Run the aggregation pipeline
  GET      `/analysis/results`     Retrieve processed results
  GET      `/analysis/locations`   Retrieve location summaries
  GET      `/metrics`              Retrieve basic metrics

Protected endpoints require `X-API-Key`. Set the key in the host
environment as `API_KEY`; never commit a real key to source control or
include it in screenshots/reports.

## Traffic record schema

-   `record_id`: integer identifier
-   `location`: location name
-   `timestamp`: ISO-compatible date/time
-   `vehicle_count`: non-negative integer
-   `avg_speed`: non-negative number

Example request body for `POST /traffic/upload`:

``` json
[
  {
    "record_id": 1,
    "location": "Clock Tower",
    "timestamp": "2026-10-11T10:00:00Z",
    "vehicle_count": 120,
    "avg_speed": 18.5
  }
]
```

## Local setup

Requirements: Python 3 and pip.

``` bash
git clone https://github.com/kraj2062/mapreduce-traffic-analyzer.git
cd mapreduce-traffic-analyzer
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

Open `http://127.0.0.1:8000/docs`. For protected requests, set an
environment variable named `API_KEY` to a unique secret before starting
the server.

## Render deployment

The deployed service uses Python 3, build command
`pip install -r requirements.txt`, and start command:

``` bash
uvicorn main:app --host 0.0.0.0 --port $PORT
```

Configure `API_KEY` in Render Environment settings. Free instances may
spin down after inactivity.

## Evaluation results

### Dataset-size benchmark (run in Google Colab)

  -----------------------------------------------------------------------
            Records     Output groups   Processing time        Throughput
                                                    (s)       (records/s)
  ----------------- ----------------- ----------------- -----------------
              1,000               144            0.0731         13,688.30

             10,000               144            0.6459         15,481.54

            100,000               144            7.7005         12,986.12
  -----------------------------------------------------------------------

Processing time increased with dataset size. These figures are
environment-specific and are not a distributed-cluster benchmark.

### API load test (50 requests per workload)

  ---------------------------------------------------------------------------
  Workload     Concurrent     Requests   Successful   Total time      Average
                  workers                                    (s) latency (ms)
  ---------- ------------ ------------ ------------ ------------ ------------
  Low                   5           50           50       0.1536        14.68

  Medium               20           50           50       0.1609        50.09

  High                 50           50           50       0.2198        66.37
  ---------------------------------------------------------------------------

### Input validation

An incomplete upload was rejected with HTTP 400
(`Missing required traffic columns`). A subsequent `/health` request
returned HTTP 200. This shows input validation and health-check
availability after a rejected request; it does not prove recovery from a
crash or database failure.

## Known limitations

-   This is MapReduce-style processing inside one Python service, not a
    multi-node Hadoop/Spark cluster.
-   The large benchmarks were run in Colab; the live Render verification
    used a small sample record.
-   Render Free does not provide a persistent disk by default, so SQLite
    data may not survive service replacement/redeployment. Persistence
    across restarts has not been established.
-   A separate Streamlit dashboard is not part of the currently deployed
    public service; Swagger is used to demonstrate the API.

## Suggested improvements

-   Use managed persistent storage or a persistent disk.
-   Add automated unit/integration tests and CI.
-   Add richer request, error, latency, and database metrics.
-   Consider distributed processing for larger workloads.
-   Add a dashboard if required by the project specification.

## Repository structure

``` text
.
├── main.py
├── mapreduce.py
├── database.py
├── requirements.txt
├── README.md
├── MapReduce_Traffic_Analyzer_Architecture.png
├── benchmark_results.csv
├── load_test_results.csv
├── failure_test.txt
└── results/
```

Update this README whenever code, configuration, endpoints, or
measurements change.

