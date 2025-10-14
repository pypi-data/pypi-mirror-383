from httpx import Response

def test_iter_results_streaming(client, router, sample_sru_xml):
    router.get("https://gallica.bnf.fr/services/engine/search/sru").mock(
        return_value=Response(200, text=sample_sru_xml)
    )
    it = client.iter_sru('dc.creator="Zola"', batch_size=2, schema="dc", limit=2)
    items = list(it)
    assert len(items) == 2
    assert all(hasattr(r, "ark") for r in items)
