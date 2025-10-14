from __future__ import annotations

"""
Ce module fournit une API orientée “document” par-dessus SRURecord.

Si tu veux rester minimaliste, tu peux ne pas l’importer ailleurs et t’en tenir
à `models.SRURecord`. Je le laisse pour coller à ton arborescence d’origine.
"""

from dataclasses import dataclass
from typing import Optional, List
from .models import SRURecord


@dataclass(slots=True)
class Record:
    ark: str
    title: Optional[str] = None
    creator: Optional[str] = None
    date: Optional[str] = None
    description: Optional[str] = None
    type: Optional[str] = None
    language: Optional[str] = None
    publisher: Optional[str] = None
    subject: List[str] = None  # type: ignore
    identifiers: List[str] = None  # type: ignore
    rights: Optional[str] = None
    source: Optional[str] = None

    @property
    def ark_url(self) -> str:
        if self.ark.startswith("http"):
            return self.ark
        return f"https://gallica.bnf.fr/{self.ark}"

    @classmethod
    def from_sru(cls, r: SRURecord) -> "Record":
        return cls(
            ark=r.ark,
            title=r.title,
            creator=r.creator,
            date=r.date,
            description=r.description,
            type=r.type,
            language=r.language,
            publisher=r.publisher,
            subject=list(r.subject),
            identifiers=list(r.identifiers),
            rights=r.rights,
            source=r.source,
        )
