import types
from pyGallica.client import GallicaClient
from pyGallica.search import build_cql

# On ne tape pas l'API réelle : on monkeypatch GallicaClient.search_sru pour renvoyer
# une SRUResult synthétique et vérifier l'itération de client.iter_sru().

class DummyRec:
    def __init__(self, i):  # i pour index
        self.ark = f"ark:/12148/btv1b{i:07d}"
        self.title = f"Doc {i}"


class DummyResult:
    def __init__(self, total, records, next_position):
        self.total = total
        self.records = records
        self.next_position = next_position


def test_iter_sru_paginates(monkeypatch):
    cli = GallicaClient()

    # 2 pages: 3 records then 2, puis fin
    pages = [
        DummyResult(5, [DummyRec(1), DummyRec(2), DummyRec(3)], next_position=4),
        DummyResult(5, [DummyRec(4), DummyRec(5)], next_position=None),
    ]
    calls = {"n": 0}

    def fake_search_sru(self, query, start, rows, schema):
        n = calls["n"]
        calls["n"] += 1
        return pages[n]

    monkeypatch.setattr(GallicaClient, "search_sru", fake_search_sru, raising=True)

    q = build_cql(title="Paris")
    got = list(cli.iter_sru(q, batch_size=3))
    assert len(got) == 5
    assert got[0].title == "Doc 1"
    assert got[-1].title == "Doc 5"
    assert calls["n"] == 2
