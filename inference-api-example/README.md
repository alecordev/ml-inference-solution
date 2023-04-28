# Inference API Example

Example to show a simple FastAPI with backend inference.

## Contents

- `api.py`: Simple FastAPI implementation.
- `rabbit.py`: Utilities to use RabbitMQ.
- `utils.py`: Simple minimal common useful functions.

## Environment Variables

In the implementation, all variables have defaults so there is no need to specify them.

Defaults from `api.py`:

```
RABBITMQ_HOST=rabbitmq
RABBITMQ_PORT=5672
RABBITMQ_USERNAME=rabbit
RABBITMQ_PASSWORD=rabbit

RABBITMQ_EXCHANGE=
RABBITMQ_EXCHANGE_TYPE=
RABBITMQ_ROUTING_KEY=pi-model-inference
RABBITMQ_ROUTING_KEY_PREDICT=api-model-inference-predict
RABBITMQ_QUEUE_NAME=api-model-inference
RABBITMQ_QUEUE_NAME_PREDICT=api-model-inference-predict
```

## Workflow

1. Start up API service. Swagger docs available by default thanks to FastAPI.
2. Receive HTTP POST request to endpoint (only `/api/v1/predict` is implemented in the example).
3. Forward the request for processing (RPC, blocking in this example) via RabbitMQ to the inference worker.
4. Return JSON output of the inference to the client.

## Food for thought

Other ideas and features that could be done easily are:

- More endpoints
- Feature to train model based on payloads
- Business logic in the API layer
- Security, performance - API_KEY, Throttling
- Handling long-running tasks (with/without additional infra)