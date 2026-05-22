import faust
import joblib
import json

app = faust.App('ml_stream_app', broker='kafka://localhost:9092')
raw_topic = app.topic('raw-data', value_type=bytes)
pred_topic = app.topic('predictions', value_type=bytes)

model = joblib.load('model.joblib')

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
