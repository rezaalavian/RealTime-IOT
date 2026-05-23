"""
prepare_and_train.py

Notebook-style data preparation and model training for the Assignment.
This script downloads the UCI Bike Sharing 'hour.csv' dataset, prepares features
(including cyclical hour encoding and categorical indicators), trains a tuned
GradientBoostingRegressor (with a RandomForest fallback), evaluates it,
saves the best model as `model.joblib`, and writes a replay CSV
`data/bike_hour_sample.csv` for the producer to replay as live events.

Run:
    python prepare_and_train.py

Outputs:
- model.joblib
- data/bike_hour_sample.csv
"""

from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.metrics import r2_score, mean_absolute_error
import joblib
import sys
import warnings
warnings.filterwarnings('ignore')


def download_and_load():
    base = "https://archive.ics.uci.edu/ml/machine-learning-databases/00275/"
    url = base + "hour.csv"
    print(f"Attempting to download dataset from {url} ...")
    try:
        df = pd.read_csv(url)
        print("Loaded rows:", len(df))
        return df
    except Exception as e:
        print('Direct CSV download failed:', e)
        zip_url = base + 'Bike-Sharing-Dataset.zip'
        print(f"Attempting to download zip from {zip_url} ...")
        try:
            import io, zipfile, urllib.request
            with urllib.request.urlopen(zip_url, timeout=30) as resp:
                data = resp.read()
            z = zipfile.ZipFile(io.BytesIO(data))
            # find hour.csv inside zip
            name = None
            for n in z.namelist():
                if n.lower().endswith('hour.csv'):
                    name = n
                    break
            if name is None:
                raise RuntimeError('hour.csv not found inside zip')
            with z.open(name) as f:
                df = pd.read_csv(f)
            print('Loaded rows from zip:', len(df))
            return df
        except Exception as e2:
            print('Failed to download and extract zip:', e2)
            raise


def prepare(df: pd.DataFrame) -> pd.DataFrame:
    # Select useful columns and rename to match producer expectations
    # hour.csv columns: instant,dteday,season,yr,hr,holiday,weekday,workingday,weathersit,temp,atemp,hum,windspeed,casual,registered,cnt
    df = df.copy()
    # keep many useful predictors from hour.csv
    cols = ['dteday','hr','season','yr','weekday','holiday','workingday','weathersit',
            'temp','atemp','hum','windspeed','cnt']
    df = df[cols]
    df = df.rename(columns={'hum': 'humidity', 'cnt': 'count', 'atemp': 'atemp'})
    # timestamp
    df['timestamp'] = pd.to_datetime(df['dteday']) + pd.to_timedelta(df['hr'], unit='h')
    # cyclical encoding for hour
    df['hr_sin'] = np.sin(2 * np.pi * df['hr'] / 24)
    df['hr_cos'] = np.cos(2 * np.pi * df['hr'] / 24)
    # ensure categorical types
    for c in ['season','weathersit','weekday','yr','holiday','workingday']:
        df[c] = df[c].astype(int)

    df = df[[
        'timestamp','hr','hr_sin','hr_cos','season','yr','weekday','holiday','workingday',
        'weathersit','temp','atemp','humidity','windspeed','count'
    ]]
    return df


def train_and_save(df: pd.DataFrame, out_dir: Path):
    # Build feature matrix with categorical encoding
    X = df.drop(columns=['timestamp','count','hr'])
    # one-hot encode categorical columns
    X = pd.get_dummies(X, columns=['season','weathersit','weekday','yr','holiday','workingday'], drop_first=True)
    y = df['count']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Try a tuned Gradient Boosting Regressor first
    gbr = GradientBoostingRegressor(random_state=42)
    param_dist = {
        'n_estimators': [100, 200, 400],
        'learning_rate': [0.01, 0.05, 0.1],
        'max_depth': [3, 5, 8],
        'subsample': [0.6, 0.8, 1.0]
    }

    search = RandomizedSearchCV(gbr, param_distributions=param_dist, n_iter=12, scoring='r2', cv=3, n_jobs=-1, random_state=42, verbose=1)
    search.fit(X_train, y_train)
    best = search.best_estimator_
    preds = best.predict(X_test)
    r2 = r2_score(y_test, preds)
    mae = mean_absolute_error(y_test, preds)
    print(f'GradientBoostingRegressor best params: {search.best_params_}')
    print('GradientBoostingRegressor R2:', r2)
    print('GradientBoostingRegressor MAE:', mae)

    # If GBR not good enough, try RandomForest with a stronger baseline
    if r2 < 0.80:
        print('GBR R2 < 0.8, trying RandomForest with basic tuning...')
        rf = RandomForestRegressor(random_state=42)
        rf_params = {'n_estimators': [200, 400], 'max_depth': [10, 20, None], 'max_features': ['sqrt', 0.5]}
        rf_search = RandomizedSearchCV(rf, param_distributions=rf_params, n_iter=6, scoring='r2', cv=3, n_jobs=-1, random_state=42, verbose=1)
        rf_search.fit(X_train, y_train)
        best_rf = rf_search.best_estimator_
        preds_rf = best_rf.predict(X_test)
        r2_rf = r2_score(y_test, preds_rf)
        mae_rf = mean_absolute_error(y_test, preds_rf)
        print(f'RandomForest best params: {rf_search.best_params_}')
        print('RandomForest R2:', r2_rf)
        print('RandomForest MAE:', mae_rf)
        # choose the better model
        if r2_rf > r2:
            best = best_rf
            r2 = r2_rf
            mae = mae_rf

    # Save the selected best model
    joblib.dump(best, out_dir / 'model.joblib')
    print('Saved model to', out_dir / 'model.joblib')
    print('Final selected model R2:', r2)
    print('Final selected model MAE:', mae)


def write_sample_csv(df: pd.DataFrame, out_path: Path, max_rows: int = 1000):
    out = out_path
    out.parent.mkdir(parents=True, exist_ok=True)
    # write a subset for replay; keep columns named temp,humidity,windspeed,count
    df_sample = df[['temp','humidity','windspeed','count']].copy()
    if len(df_sample) > max_rows:
        df_sample = df_sample.sample(n=max_rows, random_state=42).sort_index()
    df_sample.to_csv(out, index=False)
    print('Wrote replay CSV to', out)


def main():
    base = Path(__file__).resolve().parent
    data_dir = base / 'data'
    out_dir = base

    try:
        df = download_and_load()
    except Exception as e:
        print('FAILED to download dataset:', e)
        sys.exit(1)

    df_prepared = prepare(df)
    print('Prepared dataframe shape:', df_prepared.shape)

    train_and_save(df_prepared, out_dir)

    write_sample_csv(df_prepared, data_dir / 'bike_hour_sample.csv')


if __name__ == '__main__':
    main()
