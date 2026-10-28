# TopicResearcher

TopicResearcher is a FastAPI service that accepts a research topic, queues a research job for a selected Life instance, and exposes the resulting proposals through a small HTTP API.

## Features

- Lists available instances and their reachability.
- Starts instance-scoped research jobs and exposes queued proposals.
- Provides a cursor-paginated finder-compatible search endpoint.
- Keeps instance selection explicit for writes.

## Requirements

- Python 3.13
- A checkout of the Life framework beside this repository (or `LIFE_FRAMEWORK_ROOT` pointing to one)
- Docker and Docker Compose only when using the container example

## Quickstart

```bash
git clone <repository-url> topic-researcher
cd topic-researcher
cp .env.example .env

# Clone the Life framework as ../Life, then install the service dependencies.
python -m venv .venv
.venv/bin/python -m pip install -r backend/requirements.txt pytest
.venv/bin/python -m pip install ../Life/packages/shared ../Life/packages/backend-core ../Life/packages/learn-core

cd backend
../.venv/bin/python -m topic_researcher_backend
```

The API is available at `http://127.0.0.1:10052`; interactive documentation is at `/docs`.

To use Docker after the framework checkout is available, materialize its packages and start the generic example:

```bash
bash deploy/prebuild.sh
docker compose -f deploy/docker-compose.example.yml up --build
```

## Tests

Run the backend test suite from the repository root:

```bash
.venv/bin/python -m pytest -q backend/tests
```

The tests require the sibling Life framework packages listed above. GitHub Actions checks out `LIFE_FRAMEWORK_REPO` (default: `suite-life`) beside this repository before running them.

## Configuration

| Variable | Purpose |
| --- | --- |
| `PORT` | HTTP port for the backend. |
| `UVICORN_RELOAD` | Enables Uvicorn reload when set to `1`. |
| `LEARN_NODE_ID` | Node identifier used for the proposal queue. |
| `LEARN_QUEUE_ROOT` | Directory containing the proposal queue and job logs. |
| `LIFE_FRAMEWORK_ROOT` | Path to the Life framework checkout. |
| `LIFE_HOME` | Directory containing the local instance registry. |

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).
