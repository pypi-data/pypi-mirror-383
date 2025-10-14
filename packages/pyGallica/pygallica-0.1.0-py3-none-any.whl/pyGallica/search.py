from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator, Optional, List

from .models import SRURecord, SRUResult
from .exceptions import GallicaAPIError
from .parser import parse_sru_xml

# ---- CQL helpers -------------------------------------------------------------

def _quote(s: str) -> str:
    return '"' + s.replace('"', r"\"") + '"'


def cql_all(field: str, value: str) -> str:
    return f"{field} all {_quote(value)}"


def cql_any(field: str, value: str) -> str:
    return f"{field} any {_quote(value)}"


def cql_and(*clauses: str) -> str:
    clauses = [c for c in clauses if c]
    return " and ".join(f"({c})" for c in clauses)


def cql_or(*clauses: str) -> str:
    clauses = [c for c in clauses if c]
    return " or ".join(f"({c})" for c in clauses)


# ---- Recherche haut-niveau ---------------------------------------------------

def build_cql(
    *,
    title: Optional[str] = None,
    creator: Optional[str] = None,
    date: Optional[str] = None,
    doc_type: Optional[str] = None,
    language: Optional[str] = None,
    subject: Optional[str] = None,
    free: Optional[str] = None,
) -> str:
    if free:
        return free
    parts: List[str] = []
    if title:
        parts.append(cql_all("dc.title", title))
    if creator:
        parts.append(cql_all("dc.creator", creator))
    if date:
        parts.append(cql_any("dc.date", date))  # champ libre côté Gallica
    if doc_type:
        parts.append(cql_any("dc.type", doc_type))
    if language:
        parts.append(cql_any("dc.language", language))
    if subject:
        parts.append(cql_all("dc.subject", subject))
    if not parts:
        raise GallicaAPIError("At least one filter or `free` CQL must be provided.")
    return cql_and(*parts)


@dataclass(slots=True)
class SearchPaginator:
    """
    Itérateur paginé basé sur ton GallicaClient.search_sru().
    """
    client: "GallicaClient"  # forward ref pour éviter import cycle
    query: str
    page_size: int = 50
    schema: str = "dc"
    _pos: int = 1
    _finished: bool = False

    def __iter__(self):
        return self

    def __next__(self) -> SRUResult:
        if self._finished:
            raise StopIteration
        res = self.client.search_sru(self.query, start=self._pos, rows=self.page_size, schema=self.schema)
        if not res.records or not res.next_position or res.next_position <= self._pos:
            self._finished = True
        else:
            self._pos = res.next_position
        return res


def search_iter(
    client: "GallicaClient",
    *,
    title: Optional[str] = None,
    creator: Optional[str] = None,
    date: Optional[str] = None,
    doc_type: Optional[str] = None,
    language: Optional[str] = None,
    subject: Optional[str] = None,
    free_cql: Optional[str] = None,
    page_size: int = 50,
    schema: str = "dc",
    limit: Optional[int] = None,
) -> Iterator[SRURecord]:
    """
    Construit une requête CQL et itère sur les SRURecord en s’appuyant sur client.iter_sru().
    """
    q = build_cql(
        title=title,
        creator=creator,
        date=date,
        doc_type=doc_type,
        language=language,
        subject=subject,
        free=free_cql,
    )
    yield from client.iter_sru(q, batch_size=page_size, schema=schema, limit=limit)


def search_all(
    client: "GallicaClient",
    **kwargs,
) -> List[SRURecord]:
    """
    Retourne une liste concrète (pratique pour DataFrame).
    kwargs = mêmes paramètres que search_iter (title, creator, date, etc.).
    """
    return list(search_iter(client, **kwargs))
