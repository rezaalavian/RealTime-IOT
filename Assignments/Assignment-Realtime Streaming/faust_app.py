import json
import os

import joblib

from confluent_cloud import build_faust_app


app = build_faust_app('ml_stream_app')
raw_topic = app.topic('raw-data', value_type=bytes)
pred_topic = app.topic('predictions', value_type=bytes)

# Choose model path via env or use the single regression model
model_path = os.environ.get('MODEL_PATH')
if not model_path:
    if os.path.exists('model.joblib'):
        model_path = 'model.joblib'
    else:
        raise RuntimeError('No model file found (model.joblib)')

print('Loading model from', model_path)
model = joblib.load(model_path)

@app.agent(raw_topic)
async def process(stream):
    async for event in stream:
        try:
            data = json.loads(event.decode())
            features = [data.get('temp', 0), data.get('humidity', 0), data.get('windspeed', 0)]
            pred = model.predict([features])[0]
            out = {'prediction': float(pred), 'input': data}
            await pred_topic.send(value=json.dumps(out).encode())
        except Exception as e:
            print('Processing error:', e)

if __name__ == '__main__':
    app.main()
