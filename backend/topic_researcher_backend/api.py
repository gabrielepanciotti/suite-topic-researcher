"""Le rotte dell'operatore: istanze servite, ricerche in coda, lancio di una ricerca.

La ricerca vera e' `suite_learn_core research` (Life/packages/learn-core): qui
la si legge dalla coda JSONL e la si lancia come la lancia il Coordinator, con
l'istanza dichiarata. Contratto operatore: spec Life 2026-10-14 §4.
"""
from __future__ import annotations

import os
import subprocess
import sys
import uuid
from pathlib import Path
from typing import Annotated, Literal, Protocol

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from suite_learn_core.queue import JsonlQueue, ProposalQueue, ProposalStatus

from . import instances as ist
from .pagination import Pagina, decode_cursor, encode_cursor

NODE_ID = os.environ.get("LEARN_NODE_ID", "topicResearcher")

router = APIRouter(prefix="/api")


def queue_root() -> Path:
    """Radice della coda: env, altrimenti derivata dal file. Mai un assoluto."""
    env = os.environ.get("LEARN_QUEUE_ROOT")
    if env:
        return Path(env)
    return Path(__file__).resolve().parents[2] / ".learn-queue"


def get_queue() -> ProposalQueue:
    return JsonlQueue(queue_root())


class Lanciatore(Protocol):
    def __call__(self, argv: list[str], env: dict[str, str], log: Path) -> int: ...


def lancia_staccato(argv: list[str], env: dict[str, str], log: Path) -> int:
    """Il processo di ricerca, staccato dalla richiesta: torna il pid."""
    log.parent.mkdir(parents=True, exist_ok=True)
    with log.open("ab") as out:
        proc = subprocess.Popen(
            argv, env=env, stdout=out, stderr=subprocess.STDOUT,
            stdin=subprocess.DEVNULL, start_new_session=True,
        )
    return proc.pid


def get_lanciatore() -> Lanciatore:
    """Sovrascritto nei test, dove nessuna ricerca vera deve partire."""
    return lancia_staccato


# --- Istanze (spec Life 2026-10-14 §4) -------------------------------------


def _http(exc: Exception) -> HTTPException:
    if isinstance(exc, ist.IstanzaSconosciuta):
        if not exc.istanza:
            return HTTPException(422, {
                "error": "instance_required",
                "message": "dichiara `instance`: una scrittura non ha istanza di default",
                "valid": exc.validi,
            })
        return HTTPException(422, {
            "error": "instance_unknown",
            "message": str(exc),
            "valid": exc.validi,
        })
    if isinstance(exc, ist.IstanzaIrraggiungibile):
        return HTTPException(503, {
            "error": "instance_unreachable",
            "message": str(exc),
            "instance": exc.vista.id,
        })
    return HTTPException(503, f"registro delle istanze non disponibile: {exc}")


def _lettura(instance: str | None) -> str | None:
    try:
        return ist.per_lettura(instance)
    except (ist.IstanzaSconosciuta, ist.RegistroNonDisponibile) as exc:
        raise _http(exc) from exc


def _default_istanza() -> str | None:
    """Il default del device per le righe senza istanza; None se il registro non si legge."""
    try:
        return ist.default_id()
    except ist.RegistroNonDisponibile:
        return None


Istanza = Annotated[str | None, Query(description="id d'istanza; assente = tutte")]


class VistaIstanza(BaseModel):
    id: str
    status: Literal["ok", "unreachable"]
    reason: str | None = None
    default: bool = False
    profile: str = ""
    channels: dict = {}
    channel_problems: list[str] = []


@router.get("/instances", response_model=list[VistaIstanza])
def istanze() -> list[VistaIstanza]:
    """Le istanze servite: quelle irraggiungibili compaiono con il motivo, non spariscono."""
    try:
        return [VistaIstanza(**v.__dict__) for v in ist.elenco()]
    except ist.RegistroNonDisponibile as exc:
        raise _http(exc) from exc


class Proposta(BaseModel):
    id: str
    instance_id: str | None
    status: ProposalStatus
    title: str
    body: str
    source_id: str | None = None


@router.get("/research", response_model=list[Proposta])
def proposte(
    queue: Annotated[ProposalQueue, Depends(get_queue)],
    instance: Istanza = None,
    status: ProposalStatus | None = None,
) -> list[Proposta]:
    """Le proposte di ricerca, ognuna con la sua istanza (badge); `?instance=` filtra."""
    filtro = _lettura(instance)
    predefinita = _default_istanza()
    out: list[Proposta] = []
    for p in queue.list(NODE_ID, status):
        istanza = p.instance_id or predefinita
        if filtro and istanza != filtro:
            continue
        out.append(Proposta(
            id=p.id, instance_id=istanza, status=p.status, title=p.item.title,
            body=p.item.body, source_id=p.item.source_id,
        ))
    return out


@router.get("/searches", response_model=Pagina[Proposta])
def searches(
    queue: Annotated[ProposalQueue, Depends(get_queue)],
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
    cursor: str | None = None,
    instance: Istanza = None,
    status: ProposalStatus | None = None,
) -> Pagina[Proposta]:
    """The finder-compatible, cursor-paginated view of ``GET /api/research``."""
    all_items = proposte(queue=queue, instance=instance, status=status)
    offset = decode_cursor(cursor)
    items = all_items[offset:offset + limit]
    next_offset = offset + len(items)
    next_cursor = encode_cursor(next_offset) if next_offset < len(all_items) else None
    return Pagina(items=items, total=len(all_items), next_cursor=next_cursor)


class NuovaRicerca(BaseModel):
    topic: str = Field(min_length=3, max_length=500)
    instance: str | None = Field(None, description="istanza a cui va il risultato: obbligatoria")
    obiettivo: str | None = Field(None, max_length=500)


class RicercaAvviata(BaseModel):
    job: str
    instance: str
    pid: int
    log: str


@router.post("/research", response_model=RicercaAvviata, status_code=202)
@router.post("/searches", response_model=RicercaAvviata, status_code=202)
def avvia_ricerca(
    corpo: NuovaRicerca,
    lancia: Annotated[Lanciatore, Depends(get_lanciatore)],
) -> RicercaAvviata:
    """Lancia una ricerca per un'istanza: id e canali suoi nell'ambiente del processo."""
    try:
        vista = ist.per_scrittura(corpo.instance)
    except (ist.IstanzaSconosciuta, ist.IstanzaIrraggiungibile, ist.RegistroNonDisponibile) as exc:
        raise _http(exc) from exc
    root = queue_root()
    argv = [
        sys.executable, "-m", "suite_learn_core", "research", corpo.topic,
        "--node", NODE_ID, "--instance", vista.id, "--queue-root", str(root),
    ]
    if corpo.obiettivo:
        argv += ["--obiettivo", corpo.obiettivo]
    job = uuid.uuid4().hex[:12]
    log = root / "ricerche" / f"{job}.log"
    pid = lancia(argv, ist.ambiente(vista), log)
    return RicercaAvviata(job=job, instance=vista.id, pid=pid, log=log.name)
