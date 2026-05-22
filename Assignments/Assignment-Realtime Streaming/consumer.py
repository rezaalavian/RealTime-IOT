from confluent_kafka import Consumer, KafkaException
import json
import os

KAFKA_BOOTSTRAP = os.environ.get('KAFKA_BOOTSTRAP', 'localhost:9092')
TOPIC = os.environ.get('PRED_TOPIC', 'predictions')

c = Consumer({
    'bootstrap.servers': KAFKA_BOOTSTRAP,
    'group.id': 'output-consumer-group',
    'auto.offset.reset': 'earliest'
})

c.subscribe([TOPIC])
print('Subscribed to', TOPIC)

try:
    while True:
        msg = c.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            raise KafkaException(msg.error())
        data = json.loads(msg.value().decode())
        print('Prediction:', data)
except KeyboardInterrupt:
    print('Stopping')
finally:
    c.close()
