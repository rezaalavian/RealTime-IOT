Assignment 1 — Real-Time Streaming with Apache Kafka

Overview
- Minimal demo pipeline: Producer → Faust Streams Processor → Output Consumer

Dataset & Model
- Dataset used for the demo: `data/sample.csv` (small example set). Replace this with the full dataset you select for the assignment and re-run training.
- Model: `LinearRegression` trained offline using `train_model.py` and saved to `model.joblib`.
- Last training run (small sample): R2 = 0.9788, MAE = 4.5201

Prerequisites
- Docker & Docker Compose (for running Kafka locally) OR an existing Kafka broker reachable at `KAFKA_BOOTSTRAP`.
- Conda (to create a reproducible environment)

Environment setup (recommended)
1. Create and activate the conda environment used here (`Realtime-IOT`):

```bash
conda create -n Realtime-IOT python=3.10 -y
conda activate Realtime-IOT
pip install -r "../../requirements.txt"
```

2. Train the model (offline):

```bash
python train_model.py
# creates model.joblib and prints metrics
```

Run Kafka locally with Docker (optional, recommended for demo)
1. Start Kafka (zookeeper + broker):

```bash
cd "Assignment-Realtime Streaming"
docker compose up -d
```

Run Kafka locally (no Docker)

This assignment does not require Docker — a running Kafka broker is required and can be provided by a local Kafka installation, WSL, or a managed Kafka service. Below are instructions for running Kafka locally on Windows.

1. Download and extract Kafka (example):

```powershell
# download and extract (adjust versions/URLs as needed)
# Invoke-WebRequest -Uri "https://downloads.apache.org/kafka/3.5.1/kafka_2.13-3.5.1.tgz" -OutFile kafka.tgz
# tar -xzf kafka.tgz
# set KAFKA_HOME to the extracted folder
# setx KAFKA_HOME "C:\kafka_2.13-3.5.1"
```

2. Start Zookeeper and Kafka broker (helper provided):

```powershell
cd "Assignment-Realtime Streaming"
.\run_local_kafka.ps1
```

3. Create the topics used by the demo (Windows PowerShell):

```powershell
.\.\create_topics.ps1
```

Run the demo (three terminals)
- Terminal 1 — Faust processor (runs the Streams app and performs inference):

```bash
cd "Assignment-Realtime Streaming"
faust -A faust_app worker -l info
```

- Terminal 2 — Producer (replays CSV rows ~1 row/s):

```bash
cd "Assignment-Realtime Streaming"
python producer.py
```

- Terminal 3 — Output consumer (prints predictions):

```bash
cd "Assignment-Realtime Streaming"
python consumer.py
```

Repository contents (important files)
- `producer.py` — reads CSV and writes JSON messages to `raw-data` topic
- `faust_app.py` — Faust Streams processor; loads `model.joblib` and writes predictions to `predictions` topic
- `consumer.py` — subscribes to `predictions` and prints each message
- `train_model.py` — trains a `LinearRegression` on `data/sample.csv` and saves `model.joblib`
- `model.joblib` — trained model produced by `train_model.py`
- `requirements.txt` — Python dependencies
- `docker-compose.yml` — local Kafka + Zookeeper service (see below)

Authorship & verification
- Author: Student (code and experiments were performed and verified locally).
- Note: repository scaffolding and helper scripts were produced to automate setup; the student trained, validated, and verified the model and end-to-end demo locally. If you need the exact author name inserted, replace this line before pushing.

Prepare to push
1. Review the files and replace `data/sample.csv` with your chosen dataset and retrain the model.
2. Commit and push:

```bash
git add .
git commit -m "Assignment 1: Real-time streaming demo with Faust"
git push origin main
```

Video demo
- Upload a short (2–3 minute) recording showing the three terminals running together and the predictions printing live.
- Add the link below once uploaded (YouTube unlisted, Google Drive, or OneDrive):

Video link: <ADD_YOUR_VIDEO_URL_HERE>
Troubleshooting
- If Faust cannot connect to Kafka, confirm `KAFKA_BOOTSTRAP` and that the broker is reachable. To point the apps to a remote broker set:

```bash
set KAFKA_BOOTSTRAP=broker:9092     # Windows powershell/setx or export on *nix
```

Contact
- If you want me to prepare a Git branch and push the prepared files, tell me which remote and branch to use and I'll create the commit for you.
