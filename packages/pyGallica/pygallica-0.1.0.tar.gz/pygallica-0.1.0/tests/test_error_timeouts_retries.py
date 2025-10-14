import respx
from httpx import Response, ReadTimeout
import pytest

def test_timeout_raises(client, router):
    router.get("https://gallica.bnf.fr/services/engine/search/sru").mock(side_effect=ReadTimeout("t"))
    with pytest.raises(ReadTimeout):
        client.search_sru("dc.title=Paris")

def test_retry_on_5xx(client, router, sample_sru_xml):
    call = router.get("https://gallica.bnf.fr/services/engine/search/sru")
    call.side_effect = [
        Response(503, text="busy"),
        Response(200, text=sample_sru_xml),
    ]
    res = client.search_sru("q")
    assert res.total == 2

def test_404_raises(client, router):
    ark = "ark:/12148/bad"
    url = f"https://gallica.bnf.fr/iiif/{ark}/manifest.json"
    router.get(url).mock(return_value=Response(404, json={"error": "not found"}))
    with pytest.raises(FileNotFoundError):
        client.get_manifest(ark)
