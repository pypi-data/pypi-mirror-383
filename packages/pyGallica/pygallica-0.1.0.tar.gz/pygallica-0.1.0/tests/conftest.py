import pytest
import respx
import httpx

from pyGallica.client import GallicaClient

@pytest.fixture
def client():
    return GallicaClient(
        base_url="https://gallica.bnf.fr",
        sru_url="https://gallica.bnf.fr/services/engine/search/sru",
        iiif_base="https://gallica.bnf.fr/iiif",
        timeout=5.0,
        max_retries=2,
        user_agent="pyllica-tests/0.1",
    )

@pytest.fixture
def router():
    with respx.mock(assert_all_called=False) as router:
        yield router

@pytest.fixture
def http200_json():
    return {"status": "ok"}

@pytest.fixture
def sample_sru_xml():
    return """<?xml version="1.0" encoding="UTF-8"?>
<searchRetrieveResponse xmlns="http://www.loc.gov/zing/srw/">
  <version>1.1</version>
  <numberOfRecords>2</numberOfRecords>
  <records>
    <record>
      <recordSchema>dc</recordSchema>
      <recordData>
        <dc xmlns:dc="http://purl.org/dc/elements/1.1/">
          <dc:title>Document A</dc:title>
          <dc:identifier>ark:/12148/bpt6k000001</dc:identifier>
        </dc>
      </recordData>
      <recordPosition>1</recordPosition>
    </record>
    <record>
      <recordSchema>dc</recordSchema>
      <recordData>
        <dc xmlns:dc="http://purl.org/dc/elements/1.1/">
          <dc:title>Document B</dc:title>
          <dc:identifier>ark:/12148/bpt6k000002</dc:identifier>
        </dc>
      </recordData>
      <recordPosition>2</recordPosition>
    </record>
  </records>
  <nextRecordPosition>3</nextRecordPosition>
</searchRetrieveResponse>
"""

@pytest.fixture
def sample_manifest():
    return {
        "@context": "http://iiif.io/api/presentation/2/context.json",
        "@id": "https://gallica.bnf.fr/iiif/ark:/12148/bpt6k000001/manifest.json",
        "@type": "sc:Manifest",
        "label": "Document A",
        "sequences": [{
            "canvases": [
                {"@id": "c1", "label": "1", "images": [{"resource": {"@id": "p1.jpg"}}]},
                {"@id": "c2", "label": "2", "images": [{"resource": {"@id": "p2.jpg"}}]},
            ]
        }],
    }
