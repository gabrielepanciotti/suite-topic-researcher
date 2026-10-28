"""Vista configuration, with a production-safe fallback."""
from __future__ import annotations

import json
from pathlib import Path

from suite_backend_core.vista import VistaSpec


DEFAULT_VISTA = {
    "sezioni": [
        {"id": "cerca", "titolo": "Cerca", "min": "player"},
        {"id": "risultati", "titolo": "Risultati", "min": "player"},
        {"id": "salvati", "titolo": "Salvati", "min": "player"},
        {"id": "impostazioni", "titolo": "Impostazioni", "min": "admin"},
    ],
    "azioni": {
        "ricerca.crea": "creator",
        "ricerca.elimina": "admin",
        "salvato.crea": "creator",
        "salvato.modifica": "creator",
        "salvato.elimina": "creator",
        "impostazioni.modifica": "admin",
    },
}

NODE_CONFIG_PATH = Path(__file__).resolve().parents[2] / "node.config"


def load_vista_spec() -> VistaSpec:
    """Load the node vista when available, or the packaged production default."""
    if NODE_CONFIG_PATH.exists():
        node_config = json.loads(NODE_CONFIG_PATH.read_text(encoding="utf-8"))
        return VistaSpec.from_node_config(node_config)
    return VistaSpec.model_validate(DEFAULT_VISTA)
