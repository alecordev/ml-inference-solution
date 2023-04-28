import os
import sys
import json
import time
import socket
import datetime
import pathlib

import joblib

from rabbit import RPCConsumer, RabbitMQClient
from utils import now, log, get_exception_details


RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", "5672"))
RABBITMQ_USERNAME = os.getenv("RABBITMQ_USERNAME", "rabbit")
RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD", "rabbit")
RABBITMQ_QUEUE_NAME = os.getenv("RABBITMQ_QUEUE_NAME", "api-model-inference")
RABBITMQ_QUEUE_NAME_PREDICT = os.getenv(
    "RABBITMQ_QUEUE_NAME_PREDICT", "api-model-inference-predict"
)


def do_work(message):
    log(f"Received {message}")
    try:
        obj = json.loads(message)
        return json.dumps(
            {
                "date": str(now()),
                "prediction": prediction(obj).tolist(),
            }
        )
    except Exception as e:
        error = json.dumps(get_exception_details())
        log(f"Error:\n{error}")
        return error


def work():
    rpc_consumer = RPCConsumer(
        hostname=RABBITMQ_HOST,
        port=RABBITMQ_PORT,
        username=RABBITMQ_USERNAME,
        password=RABBITMQ_PASSWORD,
        queue_name=RABBITMQ_QUEUE_NAME_PREDICT,
        callback=do_work,
    )
    log(f"{SERVICE_NAME} ready and waiting for messages...")


def prediction(payload: dict = None) -> list:
    log(f"Predicting observation: {payload}")
    start = time.perf_counter()
    res = model.predict([list(payload.values())])
    log(f"Prediction took {time.perf_counter() - start:0.4f} seconds.")
    log(f"Prediction result: {res}")
    return res


def load_model():
    loaded_clf = joblib.load(
        str(
            pathlib.Path(__file__)
            .parent.parent.absolute()
            .joinpath("models", "clf_iris.joblib")
        )
    )
    return loaded_clf


if __name__ == '__main__':
    SERVICE_NAME = "Inference Service"

    log(f"Loading model...")
    start = time.perf_counter()
    model = load_model()
    log(f"Model loaded in {time.perf_counter() - start:0.6f} seconds.")

    inp = [3, 4, 4, 3]
    start = time.perf_counter()
    res = model.predict([inp])
    log(f"Single observation prediction in {time.perf_counter() - start:0.6f} seconds.")

    try:
        work()
    except Exception as e:
        error = get_exception_details()
        log(error)
