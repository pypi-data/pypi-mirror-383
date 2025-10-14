import respx
from httpx import Response

def test_get_manifest(client, router, sample_manifest):
    ark = "ark:/12148/bpt6k000001"
    url = f"https://gallica.bnf.fr/iiif/{ark}/manifest.json"
    router.get(url).mock(return_value=Response(200, json=sample_manifest))
    manifest = client.get_manifest(ark)
    assert manifest["@type"] in ("sc:Manifest", "Manifest")
    assert manifest["label"] == "Document A"
    assert len(client.list_pages_from_manifest(manifest)) == 2
