from pyGallica.search import build_cql, cql_all, cql_any, cql_and, cql_or


def test_cql_helpers_basic():
    assert cql_all("dc.title", "Paris") == 'dc.title all "Paris"'
    assert cql_any("dc.type", "image") == 'dc.type any "image"'
    q = cql_and(cql_all("dc.title", "Paris"), cql_any("dc.type", "image"))
    assert q == '(dc.title all "Paris") and (dc.type any "image")'
    q2 = cql_or(cql_any("dc.language", "fre"), cql_any("dc.language", "eng"))
    assert q2 == '(dc.language any "fre") or (dc.language any "eng")'


def test_build_cql_compound():
    q = build_cql(title="Paris", doc_type="image", date="1900", language="fre")
    assert '(dc.title all "Paris")' in q
    assert '(dc.type any "image")' in q
    assert '(dc.date any "1900")' in q
    assert '(dc.language any "fre")' in q
    assert " and " in q


def test_build_cql_free_passthrough():
    raw = '(dc.title all "Lyon") and (dc.type any "text")'
    assert build_cql(free=raw) == raw
