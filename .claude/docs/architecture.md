# TopicResearcher — architecture

## Overview

Nodo Life `topicResearcher` (`fastapi-app`, cluster `Learn`, famiglia `finder`). Un backend
FastAPI sottile sopra `suite-learn-core`: non contiene la logica di ricerca, la compone.
Il design di riferimento è la spec Life `2026-08-16-nodi-learn-researcher-extractor-design`
(nodo `topicResearcher`: decomposizione, giri di ricerca, dedup, saturazione, espansione,
giudizio, proposta). Quelle fasi sono in `learn-core`; qui non sono reimplementate.

## Componenti

- `app.py`: `create_app()` di `suite_backend_core`, `install_error_handlers`, router di
  dominio e router vista (`make_vista_router`, claims del nodo `topicResearcher`, store
  preferenze in memoria).
- `api.py`: rotte dell'operatore. `get_queue()` dà una `JsonlQueue` su `queue_root()`;
  `get_lanciatore()` dà `lancia_staccato` (sovrascritto nei test).
- `instances.py`: registro delle istanze servite. Importa `suite_core.instances` dal
  checkout di Life (`LIFE_FRAMEWORK_ROOT`, altrimenti la radice di `learn-core`). Espone
  `elenco`, `per_lettura`, `per_scrittura`, `default_id`, `ambiente`.
- `vista.py`: carica la `vista` da `node.config`, con default identico (test lo verifica).
- `pagination.py`: cursore opaco base64 url-safe di un offset; `Pagina[T]`.
- `errors.py`: busta errore `{error:{code,message,field}, detail}`, `detail` originale intatto.

## Flusso: lancio di una ricerca

1. `POST /api/research` (o alias `/api/searches`) con `topic`, `instance`, `obiettivo?`.
2. `per_scrittura` valida l'istanza: obbligatoria, registrata, raggiungibile
   (`422 instance_required|instance_unknown`, `503 instance_unreachable`).
3. Si costruisce `python -m suite_learn_core research <topic> --node <NODE_ID> --instance <id>
   --queue-root <root> [--obiettivo ...]` con l'ambiente dell'istanza: `LIFE_INSTANCE` e
   `LIFE_CHANNEL_*` suoi; `LIFE_INSTANCE_DIR` ereditato viene tolto.
4. Il processo parte staccato (`start_new_session`), log in `<queue>/ricerche/<job>.log`;
   risposta `202` con `job`, `instance`, `pid`, `log`.

## Flusso: lettura delle proposte

`queue.list(NODE_ID, status)` → ogni proposta riporta la sua istanza; senza `instance_id`
(righe anteriori al contratto) vale il default del device. `?instance=` filtra.

## Decisioni

- Una sola copia del nodo serve tutte le istanze del device (spec Life 2026-10-14 §4).
- Nessun default d'istanza in scrittura: una ricerca senza destinatario finirebbe nei dati sbagliati.
- Niente DB né frontend per ora: la fonte è la coda di `learn-core`.
- Decisione/artefatti (nota nel brain, issue) restano a `learn-core` (`review`), non a questo backend.
