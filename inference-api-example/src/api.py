import os
import sys
import json
import time
import uuid
import datetime
import traceback

import uvicorn
import fastapi
from fastapi import Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

from rabbit import RPCClient, RabbitMQClient
from utils import (
    now,
    log,
    get_exception_details,
)


RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", "5672"))
RABBITMQ_USERNAME = os.getenv("RABBITMQ_USERNAME", "rabbit")
RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD", "rabbit")

RABBITMQ_EXCHANGE = os.getenv("RABBITMQ_EXCHANGE")
RABBITMQ_EXCHANGE_TYPE = os.getenv("RABBITMQ_EXCHANGE_TYPE")
RABBITMQ_ROUTING_KEY = os.getenv("RABBITMQ_ROUTING_KEY", "api-model-inference")
RABBITMQ_ROUTING_KEY_PREDICT = os.getenv(
    "RABBITMQ_ROUTING_KEY_PREDICT", "api-model-inference-predict"
)
RABBITMQ_QUEUE_NAME = os.getenv("RABBITMQ_QUEUE_NAME", "api-model-inference")
RABBITMQ_QUEUE_NAME_PREDICT = os.getenv(
    "RABBITMQ_QUEUE_NAME_PREDICT", "api-model-inference-predict"
)

API_VERSION = "0.0.1"

app = fastapi.FastAPI()

api_v1 = fastapi.FastAPI(
    title="Model Inference API",
    description="Model Inference API",
    version=API_VERSION,
)


@app.on_event("startup")
def startup_event():
    log(dict(body="Example API Service Started", context="startup_event"))


@app.middleware("http")
async def add_context(request: fastapi.Request, call_next):
    start_time = time.time()
    request_id = str(uuid.uuid4())
    if not request.query_params.get("request_id"):
        request.state.request_id = request_id
    else:
        request.state.request_id = request.query_params["request_id"]

    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = f"{process_time:0.4f}"
    response.headers["request_id"] = request.state.request_id
    response.headers["api_version"] = API_VERSION
    return response


class IrisObservation(BaseModel):
    cw: float = 2.3
    cl: float = 2.6
    pw: float = 3
    pl: float = 3.4


@app.get("/", include_in_schema=False)
def index():
    return {"message": "ok"}


@api_v1.get("/ping", summary="Ping")
async def ping(request: Request):
    log(f"Ping endpoint requested by {request.state.request_id}")
    message = {
        "id": str(uuid.uuid4()),
        "timestamp": str(datetime.datetime.utcnow()),
        "body": "Ping endpoint requested.",
        "metadata": {
            "request_id": str(request.state.request_id),
            "client_host": str(request.client.host),
            "request_headers": str(request.headers.raw),
        },
    }
    log(json.dumps(message, indent=4))
    return {"ping": "pong"}


@api_v1.post("/predict/")
def predict(observation: IrisObservation, request: fastapi.Request):
    resp = None
    obs = observation.json()
    try:
        log(f"** Calling RPC for predict for request {request.state.request_id}...")
        log(f"* Received observation:\n{obs}")
        start = time.perf_counter()
        client = RPCClient(
            hostname=RABBITMQ_HOST,
            port=RABBITMQ_PORT,
            username=RABBITMQ_USERNAME,
            password=RABBITMQ_PASSWORD,
        )
        log(
            f"** Starting the RPC client object took: {time.perf_counter() - start:.4f}"
        )
        log("Performing inference...")
        start = time.perf_counter()
        result = client.call(
            queue_name=RABBITMQ_QUEUE_NAME_PREDICT,
            exchange_name="",
            message=obs,
        )
        resp = json.loads(result)
        log(
            f"Response received -> {resp}. Time taken: {time.perf_counter() - start:.4f}"
        )
    except Exception as e:
        error = get_exception_details()
        log(error)
    finally:
        client.close()

    if resp:
        return resp
    else:
        return JSONResponse(
            status_code=500,
            content={
                "ERROR": {
                    "error": "RPC Failed",
                    "detail": {"Error": error["message"].strip()},
                }
            },
        )


app.mount("/api/v1", api_v1)

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=int(os.getenv("API_PORT", 8000)))
