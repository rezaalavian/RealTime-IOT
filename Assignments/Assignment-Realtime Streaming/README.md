# Assignment 1 — Real-Time Streaming with Apache Kafka

## Overview
- Goal: replay dataset rows as live events, run a pre-trained ML model in a Streams processor, and publish predictions to an output topic.
- Demo components: `producer.py` → `faust_app.py` → `consumer.py`.
- Connection style: notebook-style Confluent Cloud settings using `BOOTSTRAP_SERVER`, `API_KEY`, and `API_SECRET`.
- For public repos, keep those values in `cloud_config.py` and let Git ignore it.

## Step 1 — Choose language & Streams library
- This repo uses Python + Faust (`faust-streaming`) for the Streams API.
- Faust provides `@app.agent` agents and topic streams for processing.

## Step 2 — Pick a dataset
Choose one dataset and train your ML model offline. During the demo, replay rows at about 1 row/second.

| Key | Dataset | Source | ML Task |
|------|--------|--------|---------|
| A | TIHM: Dementia Monitoring | nature.com/articles/s41597-023-02519-y | Detect agitation in PWD |
| B | Air Quality (UCI) | archive.ics.uci.edu/dataset/360 | Predict CO concentration |
| C | Credit Card Fraud | kaggle.com/datasets/mlg-ulb/creditcardfraud | Flag fraudulent transactions |
| D | Bike Sharing (UCI) | archive.ics.uci.edu/dataset/275 | Predict hourly rental count |
| E | Weather: Oshawa/Toronto | climate.weather.gc.ca | Predict next-hour temperature |

This workspace uses the UCI Bike Sharing dataset (option D). `prepare_and_train.py` downloads the data, prepares features (including cyclical hour encoding and categorical indicators), and trains a tuned Gradient Boosting regression model (with a RandomForest fallback if needed). It also writes `data/bike_hour_sample.csv` for the producer.

## Step 3 — What to build
- Producer: `producer.py` replays rows from `data/bike_hour_sample.csv` by default and publishes JSON to `raw-data`.
- Streams Processor: `faust_app.py` consumes `raw-data`, loads the regression model, runs inference, and publishes to `predictions`.
- Output Consumer: `consumer.py` reads `predictions` and prints results.
- Topic helper: `create_topics.py` creates the Cloud topics using the same notebook-style connection settings.

## Step 4 — ML model
`prepare_and_train.py` produces:
- `model.joblib` — GradientBoostingRegressor (tuned via RandomizedSearchCV)
- `data/bike_hour_sample.csv` — replay rows for the producer

Model training notes and results (example run):

- Best model: `GradientBoostingRegressor` with params `{'subsample': 0.8, 'n_estimators': 200, 'max_depth': 8, 'learning_rate': 0.05}`
- Example evaluation: **R2 = 0.9476**, **MAE = 24.54** on the held-out test set

The training pipeline will try a RandomForestRegressor if the tuned GBR does not reach a strong R2; the script saves the best performing model to `model.joblib`.

## Notebook-style connection cell
Use these names in your terminal or a small Python cell, matching the notebook style. If you prefer, place them in `cloud_config.py` in this folder; that file is ignored by Git and read automatically by the code.

```python
BOOTSTRAP_SERVER = "your-bootstrap-server"
API_KEY = "your-api-key"
API_SECRET = "your-api-secret"

KAFKA_CONFIG = {
	"bootstrap.servers": BOOTSTRAP_SERVER,
	"security.protocol": "SASL_SSL",
	"sasl.mechanisms": "PLAIN",
	"sasl.username": API_KEY,
	"sasl.password": API_SECRET,
}
```

## Quick start
1. Create and activate the conda env:

```powershell
conda create -n Realtime-IOT python=3.10 -y
conda activate Realtime-IOT
pip install -r "../../requirements.txt"
```

2. Export the notebook-style Confluent Cloud settings:

```powershell
$env:BOOTSTRAP_SERVER = "your-bootstrap-server"
$env:API_KEY = "your-api-key"
$env:API_SECRET = "your-api-secret"
```

3. Prepare data and train models:

```powershell
cd "Assignment-Realtime Streaming"
python prepare_and_train.py
```

4. Create the Cloud topics:

```powershell
python create_topics.py
```

5. Run the demo in three terminals. Start the producer first and confirm messages appear in the Confluent Cloud topic viewer before starting the processor:

```powershell
python producer.py
```

```powershell
faust -A faust_app worker -l info
```

```powershell
python consumer.py
```

If the topic viewer shows incoming messages but the processor is not running yet, that is expected. Once `faust_app.py` starts, it will consume the queued records and publish predictions.

## Files of interest
- `prepare_and_train.py` — notebook-style script that downloads the dataset, prepares features (including cyclical hour encoding), trains a tuned `GradientBoostingRegressor` (with RF fallback), saves `model.joblib`, and writes `data/bike_hour_sample.csv`.
- `producer.py` — uses `INPUT_CSV` or `data/bike_hour_sample.csv`.
- `faust_app.py` — Faust Streams processor; loads the model from `MODEL_PATH` or uses `model.joblib`.
- `consumer.py` — prints predictions from `predictions`.
- `confluent_cloud.py` — shared helper for notebook-style Confluent Cloud settings.
- `create_topics.py` — creates `raw-data` and `predictions` in Confluent Cloud.
- `cloud_config.py` — private file for your bootstrap server, API key, and API secret. Keep it out of Git.

## Deliverables mapping
| Item | What to include |
|------|-----------------|
| Source code | `producer.py`, `faust_app.py`, `consumer.py`, `prepare_and_train.py` |
| Trained model | `model.joblib` |
| Dependencies | `requirements.txt` |
| README | This file |
| Video demo | 2–3 minute recording showing the three terminals |

Video demo link: 'https://drive.google.com/file/d/1zInZaz1w5ETdWq2W_ZLbZ35f7LcxVwsE/view?usp=drive_link'
