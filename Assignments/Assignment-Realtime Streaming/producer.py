import csv
import json
import os
import time

from confluent_kafka import Producer

from confluent_cloud import build_kafka_config


TOPIC = os.environ.get('RAW_TOPIC', 'raw-data')

p = Producer(build_kafka_config())

def delivery_report(err, msg):
    if err is not None:
        print('Delivery failed:', err)

if __name__ == '__main__':
    # Use the replay CSV created by prepare_and_train.py.
    csvfile = os.environ.get('INPUT_CSV', 'data/bike_hour_sample.csv')
    with open(csvfile, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            payload = json.dumps({k: float(v) if v.replace('.','',1).isdigit() else v for k,v in row.items()})
            p.produce(TOPIC, payload.encode('utf-8'), callback=delivery_report)
            p.flush()
            print('Sent', payload)
            time.sleep(1)
