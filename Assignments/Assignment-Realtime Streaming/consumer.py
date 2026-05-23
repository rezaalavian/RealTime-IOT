import json
import os

from confluent_kafka import Consumer, KafkaException

from confluent_cloud import build_kafka_config


TOPIC = os.environ.get('PRED_TOPIC', 'predictions')

c = Consumer({
    **build_kafka_config(),
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
