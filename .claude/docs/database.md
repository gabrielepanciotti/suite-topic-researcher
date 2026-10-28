# TopicResearcher — database

## Stato

Il nodo **non usa oggi alcun database**. Esiste lo scaffold Alembic (`backend/alembic.ini`,
`backend/migrations/env.py`, `versions/` vuota) e `asyncpg` in `requirements.txt`, ma nessun
modello né migrazione. La porta db assegnata dal registro Life è `11164`, non ancora usata.

## Dove stanno i dati

La coda delle proposte è un archivio JSONL di `suite_learn_core.queue.JsonlQueue`, in
`LEARN_QUEUE_ROOT` (default `backend/.learn-queue`, derivato da `api.py`; dati locali). Ogni proposta ha: `id`, `status` (`ProposalStatus`),
`instance_id`, `item` (`title`, `body`, `source_id`). I log dei processi di ricerca sono in
`<root>/ricerche/<job>.log`.

## Migrazione `assegna_istanza`

`scripts/utility/assegna_istanza.py [--instance ID] [--dry-run]` aggiunge `instance_id` alle
proposte scritte prima del contratto operatore. Additiva, copia ogni file in
`<file>.bak-<data>-prima-istanza`, lascia com'è una riga illeggibile. Senza `--instance`
vale il default del device.

## Regole

- Ogni nodo possiede i suoi dati; cross-nodo solo via API.
- Se arriverà un DB: Alembic additivo, mai ALTER manuali, mai DROP senza backup.
  Le tabelle standard della famiglia `finder` sono in Life `docs/standards/finder.md` §10.
