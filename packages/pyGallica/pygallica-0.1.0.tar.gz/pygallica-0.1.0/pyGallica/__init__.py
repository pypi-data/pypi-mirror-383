from __future__ import annotations

from .client import GallicaClient, validate_ark
from .search import (
    build_cql,
    cql_all, cql_any, cql_and, cql_or,
    search_iter, SearchPaginator, search_all,
)
from .parser import parse_sru_xml, records_to_json, records_to_dataframe
from .models import SRURecord, SRUResult, IIIFPage
from .exceptions import GallicaError, GallicaHTTPError, GallicaAPIError, GallicaParseError

__all__ = [
    "GallicaClient", "validate_ark",
    "build_cql", "cql_all", "cql_any", "cql_and", "cql_or",
    "search_iter", "search_all", "SearchPaginator",
    "SRURecord", "SRUResult", "IIIFPage",
    "parse_sru_xml", "records_to_json", "records_to_dataframe",
    "GallicaError", "GallicaHTTPError", "GallicaAPIError", "GallicaParseError",
]

__version__ = "0.1.0"