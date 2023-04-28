# Inference worker example

Example service providing the backend inference implementation for an API.

Receives and processes RabbitMQ messages.

## Contents

- `inference_service.py`: Implementation of the worker, which processes RabbitMQ messages to perform an inference from.
- `model.py` is provided to see how the model was trained and generated. This helps show that any model can be trained and loaded, regardless of the library.

The following are exactly the same as the ones present in `inference-api-example` service:

- `rabbit.py`: Utilities to use RabbitMQ.
- `utils.py`: Simple minimal common useful functions.

## Environment Variables

Defaults set by `inference_service.py`:

```
RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672
RABBITMQ_USERNAME=rabbit
RABBITMQ_PASSWORD=rabbit

RABBITMQ_QUEUE_NAME=api-model-inference
RABBITMQ_QUEUE_NAME_PREDICT=api-model-inference-predict
```

## Workflow

1. Start up (connect and listen to RabbitMQ queue)
2. Process message received by performing an inference on the content
3. Return the inference results

## Food for thought

This can easily be extended to add:

- Business logic (filters and evaluation based on message contents)
- New functionalities (e.g. training based on message payloads, listing models' versions, dynamically loading models as defined in the API, etc)
- Refactoring and possibilities when using `mlflow`, `S3` and custom solutions for MLOps.