import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_absolute_error
import joblib

# Train a simple linear regression on sample.csv
if __name__ == '__main__':
    df = pd.read_csv('data/sample.csv')
    X = df[['temp', 'humidity', 'windspeed']]
    y = df['count']
    model = LinearRegression()
    model.fit(X, y)
    preds = model.predict(X)
    print('R2:', r2_score(y, preds))
    print('MAE:', mean_absolute_error(y, preds))
    joblib.dump(model, 'model.joblib')
    print('Saved model.joblib')
