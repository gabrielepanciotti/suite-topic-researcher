# TopicResearcher — api

Backend FastAPI (porta `10052`). Docs interattive su `/docs`. Errori: busta
`{"error":{"code","message","field"},"detail":...}`.

## Rotte presenti

| Rotta | Scopo |
|---|---|
| `GET /api/health`, `GET /health` | health (da `backend-core`) |
| `GET /api/vista` | sezioni e azioni per ruolo (`make_vista_router`) |
| `GET /api/instances` | istanze servite con `status` `ok`/`unreachable` e motivo, canali, default |
| `GET /api/research?instance=&status=` | proposte con badge istanza (lista semplice) |
| `GET /api/searches?limit=&cursor=&instance=&status=` | stessa vista, paginata `{items,total,next_cursor}`; `limit` 1-200 (default 50) |
| `POST /api/research`, `POST /api/searches` | lancia una ricerca: `{topic (3-500), instance, obiettivo?}` → `202 {job,instance,pid,log}` |

Errori del `POST`: `422 instance_required` (manca `instance`), `422 instance_unknown`
(porta `valid`), `503 instance_unreachable`. Un cursore non valido dà `422`.

## Confronto con lo standard `finder` (Life `docs/standards/finder.md` §9)

| Rotta standard | Stato |
|---|---|
| `POST /api/searches` | **presente**, ma lancia un processo asincrono e non un record: niente `ricerca.crea` via `require_action`, niente id di ricerca |
| `GET /api/searches` | **presente** (paginata); elenca proposte, non ricerche; filtro `status` è lo stato della proposta |
| `GET /api/searches/{id}` | **manca** |
| `GET /api/searches/{id}/results` | **manca** |
| `DELETE /api/searches/{id}` | **manca** |
| `GET /api/saved`, `POST`, `PATCH /{id}`, `DELETE /{id}` | **mancano** (nessun salvato, nessun DB) |
| `GET /api/health` | presente |
| `GET /api/vista` | presente |
| `GET /overview` | **non verificato** nel nodo: non è aggiunto da `app.py`, dipende da `create_app` |
| `require_action` sulle scritture | **manca**: `POST` non controlla i ruoli |
| Filtri `q`, `sort`, `min_price` | **mancano** (solo `instance`, `status`) |

Fuori standard, specifiche del nodo: `/api/instances`, `/api/research`, parametro `instance`.
