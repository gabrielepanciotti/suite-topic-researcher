# TopicResearcher — deployment

Stato: **non in produzione** (`docs/guida.md`). Gli artefatti in `deploy/` sono generati dal
conform (`suite.lock.json`): non si editano; gli override locali vanno in
`deploy/docker-compose.override.yml`.

## Dev locale

```bash
cp .env.example .env
python -m venv .venv
.venv/bin/python -m pip install -r backend/requirements.txt pytest
# poi shared, backend-core, learn-core dal checkout di Life accanto al repo
cd backend && ../.venv/bin/python -m topic_researcher_backend
```

## Docker

- `bash deploy/build.sh [--prod]` (prebuild dei package Life in `backend/vendor/` + build)
- `bash deploy/compose.sh [--prod] up -d`: unico modo corretto di lanciare compose
- Servizio `topicresearcher-backend`, rete esterna `personal-net`, healthcheck su `/api/health`.
- Dev: `10252:10052`, monta `backend/` e `node.config`. Prod: `LIFE_INSTANCE` (default
  `personal`) e `LIFE_GATE_JWKS_URL` nell'ambiente, nessuna porta pubblicata.
- Vhost `topic-researcher.life.local` → `topicresearcher-backend:10052` (`deploy/Caddyfile`).
- Go-live standard: `python -m suite_core.nodes go-live <repo>`.

## Variabili (`.env.example`)

`PORT`, `UVICORN_RELOAD`, `LEARN_NODE_ID`, `LEARN_QUEUE_ROOT`, `LIFE_FRAMEWORK_ROOT`.

## Da tenere presente

Il backend lancia `suite_learn_core` come sottoprocesso e legge il registro istanze di Life
(`~/.life/instances.json` o `$LIFE_HOME`): nel container servono il package e quel registro
montati, o il lancio risponde `503`. Non verificato in questo repo.

## CI

`.github/workflows/ci.yml`: checkout del repo e del framework (`LIFE_FRAMEWORK_REPO`,
default `suite-life`), Python 3.13, installazione dei package, pytest.
