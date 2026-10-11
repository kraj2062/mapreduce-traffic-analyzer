# mapreduce-traffic-analyzer
Cloud-based traffic analytics using MapReduce principles and REST APIs.
# MapReduce Traffic Analyzer

## Project Overview
The MapReduce Traffic Analyzer processes traffic records and identifies congestion patterns by location and hour.

## Technologies
- Python
- Pandas and NumPy
- FastAPI
- SQLite
- Matplotlib
- Google Colab

## Main Features
- Synthetic traffic data generation
- Map, Shuffle/Group and Reduce processing
- Traffic summaries by location and hour
- REST APIs for uploads, analysis, results and metrics
- API-key authentication and input validation
- Dataset performance benchmarking and API load testing

## Project Structure
- `main.py` — FastAPI application
- `mapreduce.py` — traffic processing pipeline
- `database.py` — SQLite database operations
- `requirements.txt` — Python dependencies
- `MapReduce_Traffic_Analyzer.ipynb` — development notebook

## Running Locally
Install dependencies:

`pip install -r requirements.txt`

Set an API key in your environment, then run:

`uvicorn main:app --reload`

Open `/docs` on your local server to inspect and test the API.

## Experimental Results
The recorded benchmark processed 100,000 records in 7.7005 seconds. The API load test completed 150 health-check requests across three concurrency levels.

## Project Status
The processing pipeline and API have been tested in Google Colab. Public cloud deployment and distributed multi-machine execution require separate implementation and verification.
