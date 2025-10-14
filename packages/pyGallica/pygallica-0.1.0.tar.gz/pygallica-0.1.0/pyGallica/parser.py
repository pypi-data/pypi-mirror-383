from __future__ import annotations

from typing import Tuple, List, Dict, Any, Optional, Iterable
from xml.etree import ElementTree as ET

try:
    import pandas as pd  # optionnel
except Exception:  # pragma: no cover
    pd = None  # type: ignore

from .models import SRURecord
from .exceptions import GallicaAPIError, GallicaParseError

NS = {
    "sru": "http://www.loc.gov/zing/srw/",
    "dc": "http://purl.org/dc/elements/1.1/",
    "oai_dc": "http://www.openarchives.org/OAI/2.0/oai_dc/",
}


def _texts(node: ET.Element, path: str) -> List[str]:
    return [e.text.strip() for e in node.findall(path, NS) if e is not None and e.text]


def _first(node: ET.Element, path: str) -> Optional[str]:
    vals = _texts(node, path)
    return vals[0] if vals else None


def parse_dc_container(dc_node: ET.Element) -> SRURecord:
    """
    Parse un conteneur DC (<oai_dc:dc> ou un bloc recordData avec des dc:*) en SRURecord enrichi.
    """
    title = _first(dc_node, ".//dc:title")
    creator = _first(dc_node, ".//dc:creator")
    date = _first(dc_node, ".//dc:date")
    description = _first(dc_node, ".//dc:description")
    rtype = _first(dc_node, ".//dc:type")
    lang = _first(dc_node, ".//dc:language")
    publisher = _first(dc_node, ".//dc:publisher")
    rights = _first(dc_node, ".//dc:rights")
    source = _first(dc_node, ".//dc:source")
    subjects = _texts(dc_node, ".//dc:subject")
    identifiers = _texts(dc_node, ".//dc:identifier")

    # Heuristique pour récupérer l'ARK
    ark: Optional[str] = None
    for ident in identifiers:
        if ident.startswith("ark:") or "gallica.bnf.fr/ark:" in ident:
            ark = ident.split("gallica.bnf.fr/")[-1] if "gallica.bnf.fr/" in ident else ident
            break
        if ident.startswith("http") and "gallica.bnf.fr/ark:" in ident:
            ark = ident.split("gallica.bnf.fr/")[-1]
            break
    if not ark:
        # fallback minimal : prends le premier identifier si on n'a rien
        ark = identifiers[0] if identifiers else None

    if not ark and not title:
        raise GallicaParseError("Record sans champ minimal (title/identifier).")

    return SRURecord(
        ark=ark or "",
        title=title,
        creator=creator,
        date=date,
        description=description,
        type=rtype,
        language=lang,
        publisher=publisher,
        subject=subjects,
        identifiers=identifiers,
        rights=rights,
        source=source,
        _raw_xml=ET.tostring(dc_node, encoding="unicode"),
    )


def parse_sru_xml(xml_text: str) -> Tuple[List[SRURecord], Dict[str, Any]]:
    """
    Parse une réponse SRU XML complète en liste de `SRURecord` + meta.
    """
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError as e:
        raise GallicaParseError(f"Invalid XML: {e}") from e

    # Diagnostics SRU ?
    diag = root.find(".//sru:diagnostics", NS)
    if diag is not None:
        details: Dict[str, str] = {}
        for d in diag.findall(".//sru:diagnostic", NS):
            uri = (d.findtext("sru:uri", default="", namespaces=NS) or "").strip()
            msg = (d.findtext("sru:message", default="", namespaces=NS) or "").strip()
            details[uri] = msg
        raise GallicaAPIError("SRU returned diagnostics", diagnostics=details)

    number_text = root.findtext(".//sru:numberOfRecords", default="", namespaces=NS)
    total = int(number_text) if number_text.isdigit() else 0

    next_pos_text = root.findtext(".//sru:nextRecordPosition", default="", namespaces=NS)
    next_pos = int(next_pos_text) if next_pos_text.isdigit() else None

    records: List[SRURecord] = []
    for rec in root.findall(".//sru:record", NS):
        dc_root = rec.find(".//oai_dc:dc", NS)
        if dc_root is None:
            # parfois les dc:* sont directement sous recordData
            dc_root = rec.find(".//sru:recordData", NS) or rec
        try:
            records.append(parse_dc_container(dc_root))
        except GallicaParseError:
            # on skippe gracieux
            continue

    meta = {"numberOfRecords": total, "nextRecordPosition": next_pos}
    return records, meta


def records_to_json(records: Iterable[SRURecord]) -> List[Dict[str, Any]]:
    return [
        {
            "ark": r.ark,
            "ark_url": r.ark_url,
            "title": r.title,
            "creator": r.creator,
            "date": r.date,
            "description": r.description,
            "type": r.type,
            "language": r.language,
            "publisher": r.publisher,
            "subject": r.subject,
            "identifiers": r.identifiers,
            "rights": r.rights,
            "source": r.source,
        }
        for r in records
    ]


def records_to_dataframe(records: Iterable[SRURecord]):
    if pd is None:
        raise ImportError("pandas is not installed. `pip install pandas` to use this feature.")
    return pd.DataFrame(records_to_json(records))
