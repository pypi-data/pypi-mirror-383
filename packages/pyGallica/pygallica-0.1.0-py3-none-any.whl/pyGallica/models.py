from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


@dataclass(slots=True)
class SRURecord:
    """Minimal SRU record as returned by your client.search_sru()."""
    ark: str
    title: Optional[str] = None
    # Optional expanded DC fields (filled by parser if you l’utilises)
    creator: Optional[str] = None
    date: Optional[str] = None
    description: Optional[str] = None
    type: Optional[str] = None
    language: Optional[str] = None
    publisher: Optional[str] = None
    subject: List[str] = field(default_factory=list)
    identifiers: List[str] = field(default_factory=list)
    rights: Optional[str] = None
    source: Optional[str] = None
    _raw_xml: Optional[str] = None  # debug

    @property
    def ark_url(self) -> str:
        # accepte soit "ark:/..." soit une URL complète
        if self.ark.startswith("http"):
            return self.ark
        return f"https://gallica.bnf.fr/{self.ark}"


@dataclass(slots=True)
class SRUResult:
    total: int
    records: List[SRURecord]
    next_position: Optional[int] = None


@dataclass(slots=True)
class IIIFPage:
    """Petit modèle utilitaire si tu veux typer les pages extraites d’un manifest."""
    id: str
    label: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    thumbnails: List[Dict[str, Any]] = field(default_factory=list)
