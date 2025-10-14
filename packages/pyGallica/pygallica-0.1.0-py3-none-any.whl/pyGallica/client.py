from __future__ import annotations
import re
import time
from typing import Iterable, Optional, Dict, Any, List
import httpx
from .models import SRURecord, SRUResult
from xml.etree import ElementTree as ET

NS_SRU = {"sru": "http://www.loc.gov/zing/srw/", "dc": "http://purl.org/dc/elements/1.1/"}
_ARK_RE = re.compile(r"^ark:/\d{5}/[a-z0-9]+", re.I)

def validate_ark(ark: str) -> bool:
    if not _ARK_RE.match(ark or ""):
        raise ValueError("Invalid ARK")
    return True

class GallicaClient:
    def __init__(
        self,
        base_url: str = "https://gallica.bnf.fr",
        sru_url: str = "https://gallica.bnf.fr/services/engine/search/sru",
        iiif_base: str = "https://gallica.bnf.fr/iiif",
        timeout: float = 10.0,
        max_retries: int = 2,
        user_agent: str = "pyGallica/0.1",
    ):
        if timeout <= 0:
            raise ValueError("timeout must be > 0")
        self.base_url = base_url.rstrip("/")
        self.sru_url = sru_url
        self.iiif_base = iiif_base.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self.user_agent = user_agent
        self._client = httpx.Client(timeout=timeout, headers=self._headers())

    def _headers(self) -> Dict[str, str]:
        return {"User-Agent": self.user_agent, "Accept": "*/*"}

    def _request(self, method: str, url: str, **kw) -> httpx.Response:
        retries = 0
        while True:
            try:
                r = self._client.request(method, url, **kw)
                if r.status_code >= 500 and retries < self.max_retries:
                    retries += 1
                    time.sleep(0.1 * retries)
                    continue
                if r.status_code == 404:
                    raise FileNotFoundError(url)
                r.raise_for_status()
                return r
            except httpx.ReadTimeout:
                raise

    def search_sru(self, query: str, start: int = 1, rows: int = 10, schema: str = "dc") -> SRUResult:
        params = {"query": query, "startRecord": start, "maximumRecords": rows, "recordSchema": schema}
        r = self._request("GET", self.sru_url, params=params)
        root = ET.fromstring(r.text)

        total = int(root.findtext("sru:numberOfRecords", namespaces=NS_SRU) or 0)
        next_pos_text = root.findtext("sru:nextRecordPosition", namespaces=NS_SRU)
        next_pos = int(next_pos_text) if next_pos_text else None

        recs: List[SRURecord] = []
        for rec in root.findall("sru:records/sru:record", namespaces=NS_SRU):
            # 👉 Sois tolérant : prends recordData comme conteneur et cherche dc:* à l’intérieur,
            #    qu’il y ait <dc:dc>, <oai_dc:dc> ou juste <dc> sans namespace.
            recdata = rec.find("sru:recordData", namespaces=NS_SRU)
            if recdata is None:
                continue

            # Titre
            title = recdata.findtext(".//dc:title", namespaces=NS_SRU)

            # Identifiers (prends le premier non vide)
            id_elems = recdata.findall(".//dc:identifier", namespaces=NS_SRU)
            ark = None
            for e in id_elems:
                if e is not None and e.text:
                    ark = e.text.strip()
                    break

            if ark:
                recs.append(SRURecord(ark=ark, title=title))

        return SRUResult(total=total, records=recs, next_position=next_pos)


    def iter_sru(self, query: str, batch_size: int = 50, schema: str = "dc", limit: Optional[int] = None):
        yielded = 0
        pos = 1
        while True:
            res = self.search_sru(query, start=pos, rows=batch_size, schema=schema)
            for r in res.records:
                yield r
                yielded += 1
                if limit and yielded >= limit:
                    return
            if not res.next_position or not res.records:
                return
            pos = res.next_position

    def get_metadata(self, ark: str) -> Dict[str, Any]:
        validate_ark(ark)
        url = f"{self.base_url}/services/OAIRecord"
        r = self._request("GET", url, params={"ark": ark})
        return r.json()

    def get_manifest(self, ark: str) -> Dict[str, Any]:
        validate_ark(ark)
        url = f"{self.iiif_base}/{ark}/manifest.json"
        return self._request("GET", url).json()

    def list_pages_from_manifest(self, manifest: Dict[str, Any]) -> List[Dict[str, Any]]:
        seqs = manifest.get("sequences", [])
        if not seqs:
            return []
        return seqs[0].get("canvases", [])

    def get_thumbnail(self, ark: str, page: int = 1, max_width: int = 200) -> bytes:
        validate_ark(ark)
        url = f"{self.iiif_base}/{ark}/f{page}/full/{max_width},/0/default.jpg"
        return self._request("GET", url).content

    def get_page_image(self, ark: str, page: int, max_width: int = 1000) -> bytes:
        validate_ark(ark)
        url = f"{self.iiif_base}/{ark}/f{page}/full/{max_width},/0/default.jpg"
        return self._request("GET", url).content
