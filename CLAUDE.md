# TopicResearcher — nodo Life

> Nodo `topicResearcher`, tipo `fastapi-app`, cluster `Learn`, famiglia `finder`, host
> `topic-researcher.life.local`. Eredita da Life via `inherits` (`../Life/node.config`).
> Repo pubblico: niente dati personali, path assoluti, host interni o segreti.

## Cos'è

Servizio FastAPI che riceve un argomento, lancia una ricerca per una **istanza Life
dichiarata** e mostra le proposte prodotte. La ricerca vera è `python -m suite_learn_core
research` (package `learn-core` di Life); qui ci sono solo le rotte dell'operatore: elenco
istanze, lettura della coda delle proposte, lancio staccato del processo di ricerca.
Non chiama direttamente alcun modello LLM.

Guida d'uso: `docs/guida.md`. Dettagli: `.claude/docs/` (architecture, database, api,
deployment, backlog).

## Stato reale

- Backend con rotte di dominio (`/api/instances`, `/api/research`, `/api/searches`) più
  `/api/vista` e `/api/health` da `backend-core`.
- Nessun frontend, nessun database in uso (Alembic è solo lo scaffold, nessuna migrazione).
- Non è in produzione; il catalogo ricercabile di pagine e siti (ex `webCataloger`) non c'è.
- Non ha un bot Telegram proprio: si raggiunge dal menu del bot radice del Coordinator.

## Struttura

| Percorso | Contenuto |
|---|---|
| `backend/topic_researcher_backend/` | `app.py` (create_app + vista), `api.py` (rotte), `instances.py` (registro istanze), `vista.py`, `pagination.py`, `errors.py` |
| `backend/tests/` | pytest: istanze, ricerche, vista, migrazione `assegna_istanza` |
| `backend/migrations/` | scaffold Alembic, nessuna revisione |
| `scripts/utility/assegna_istanza.py` | rietichetta le proposte pre-contratto con la loro istanza |
| `deploy/`, `suite.lock.json`, `.ai/`, `.claude/agents/` | **generati** dal conform: non si editano a mano |
| `brain/` | wiki del nodo (solo `README.md` tracciato) |
| `forge.status.json`, `.claude/coordinator.toml` | stato Forge e manifesto Coordinator |

## Comandi

```bash
cd backend && ../.venv/bin/python -m topic_researcher_backend   # porta 10052 (PORT)
.venv/bin/python -m pytest -q backend/tests                      # dalla root
bash deploy/build.sh && bash deploy/compose.sh up -d             # Docker (dev)
```

Serve un checkout di Life accanto al repo (o `LIFE_FRAMEWORK_ROOT`) con `shared`,
`backend-core`, `learn-core` installati nel venv.

## Regole del nodo

- **Istanza esplicita in scrittura**: `POST` senza `instance` valida risponde `422`; mai un
  default del device. In lettura `?instance=` assente = tutte le istanze.
- Le istanze si leggono solo con `suite_core.instances` (lettore unico di Life), mai con un
  parsing proprio del registro.
- Le proposte vivono nella coda JSONL di `learn-core` (`LEARN_QUEUE_ROOT`), non in un DB.
- Un componente per passo: il lancio del processo è dietro `get_lanciatore`, sostituibile nei test.
- Mai path assoluti nei file versionati: radici derivate da `__file__` o da env.
- Python 3.13 in `.venv/`, mai pip globale. Niente `print`: `logging`.
- Test e lint (`ruff.toml`) prima di dichiarare finito; nessun commit di `.env`.

## Porte

Backend `10052` (host `10252` nel compose dev), frontend previsto `3386`, db `11164`
(registro Life `docs/ports.registry.json`, id `topicResearcher`).

## Backlog

Solo issue GitHub del repo: vedi `.claude/docs/backlog.md`.
