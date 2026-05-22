# RealTime-IOT

Overview
- Collection of demo projects and assignments for the Real-Time Data Analytics (IoT) course.

Repository structure
- `Assignment-Realtime Streaming/` — Assignment 1: Kafka + Faust streaming demo (producer, streams processor, consumer, training script)
- Additional notebooks and example scripts are stored at the workspace root.

Quick start (recommended)
1. Open a terminal and change to this repository root:

```powershell
cd "c:\Users\73rez\OneDrive\Desktop\My cources\Real-Time Data Analytics IoT\Repository\RealTime-IOT"
```

2. Create the Conda environment from the provided `environment.yml` (preferred):

```bash
conda env create -f environment.yml
conda activate Realtime-IOT
```

Or create manually and install from `requirements.txt`:

```bash
conda create -n Realtime-IOT python=3.10 -y
conda activate Realtime-IOT
pip install -r requirements.txt
```

3. Run the Assignment-Realtime Streaming demo (recommended flow):

- Start Kafka locally (uses the assignment's docker compose):

```bash
cd "..\..\Assignment-Realtime Streaming"
docker compose up -d
```

- Create topics (PowerShell helper):

```powershell
.\create_topics.ps1
```

- Train the model (offline):

```bash
python train_model.py
```

- Open three terminals and run:

Terminal A (Faust processor):
```bash
faust -A faust_app worker -l info
```

Terminal B (Producer):
```bash
python producer.py
```

Terminal C (Consumer):
```bash
python consumer.py
```

Notes
- The `Assignment-Realtime Streaming` folder contains full instructions, a `docker-compose.yml` to run Kafka locally, and a `create_topics.ps1` helper for Windows.
- Replace `data/sample.csv` with your selected full dataset and re-run `train_model.py` to generate a production model file.

Preparing to push
- Review files, run the demo locally, then commit and push:

```bash
git add .
git commit -m "Add RealTime-IOT demos and setup files"
git push origin main
```

If you want, I can create the commit locally and push if you provide the remote name and branch.
 
Video demo link
- Add a link to your demo video (YouTube unlisted, Google Drive, or OneDrive) in the assignment README under "Video link" before pushing the repository.

