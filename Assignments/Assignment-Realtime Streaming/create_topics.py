from confluent_kafka.admin import AdminClient, NewTopic

from confluent_cloud import DEFAULT_TOPIC_NAMES, build_kafka_config


if __name__ == "__main__":
    config = build_kafka_config()
    admin = AdminClient(config)
    # Confluent Cloud requires replication_factor=3 for topics
    rf = int(__import__('os').environ.get('TOPIC_REPLICATION_FACTOR', '3'))
    topics = [NewTopic(name, num_partitions=1, replication_factor=rf) for name in DEFAULT_TOPIC_NAMES]
    result = admin.create_topics(topics)
    for topic_name, future in result.items():
        try:
            future.result()
            print(f"Created topic: {topic_name}")
        except Exception as exc:
            if "already exists" in str(exc).lower():
                print(f"Topic already exists: {topic_name}")
            else:
                raise
