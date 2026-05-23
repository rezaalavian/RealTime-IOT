import os
import ssl

import faust

try:
    from cloud_config import API_KEY, API_SECRET, BOOTSTRAP_SERVER  # type: ignore
except ImportError:
    API_KEY = os.environ.get("API_KEY") or os.environ.get("KAFKA_API_KEY")
    API_SECRET = os.environ.get("API_SECRET") or os.environ.get("KAFKA_API_SECRET")
    BOOTSTRAP_SERVER = os.environ.get("BOOTSTRAP_SERVER") or os.environ.get("KAFKA_BOOTSTRAP")

DEFAULT_TOPIC_NAMES = ("raw-data", "predictions")


def load_cloud_settings():
    bootstrap_server = BOOTSTRAP_SERVER
    api_key = API_KEY
    api_secret = API_SECRET
    if not bootstrap_server:
        raise RuntimeError("BOOTSTRAP_SERVER is required")
    if not api_key:
        raise RuntimeError("API_KEY is required")
    if not api_secret:
        raise RuntimeError("API_SECRET is required")
    return bootstrap_server, api_key, api_secret


def build_kafka_config():
    bootstrap_server, api_key, api_secret = load_cloud_settings()
    return {
        "bootstrap.servers": bootstrap_server,
        "security.protocol": "SASL_SSL",
        "sasl.mechanisms": "PLAIN",
        "sasl.username": api_key,
        "sasl.password": api_secret,
    }


def build_faust_app(app_id: str) -> faust.App:
    bootstrap_server, api_key, api_secret = load_cloud_settings()
    ssl_context = ssl.create_default_context()
    credentials = faust.SASLCredentials(
        username=api_key,
        password=api_secret,
        ssl_context=ssl_context,
    )
    return faust.App(
        app_id,
        broker=f"kafka://{bootstrap_server}",
        broker_credentials=credentials,
    )
