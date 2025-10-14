import respx
from httpx import Response

def test_get_record_metadata(client, router):
    ark = "ark:/12148/bpt6k000001"
    url = f"https://gallica.bnf.fr/services/OAIRecord?ark={ark}"
    router.get(url).mock(return_value=Response(200, json={"ark": ark, "title": "Document A"}))
    md = client.get_metadata(ark)
    assert md["ark"] == ark
    assert md["title"] == "Document A"
