from click.testing import CliRunner
from pyGallica.cli import cli
import respx
from httpx import Response

def test_cli_search_json(router):
    runner = CliRunner()
    xml = """<?xml version="1.0"?><searchRetrieveResponse xmlns="http://www.loc.gov/zing/srw/"><version>1.1</version><numberOfRecords>1</numberOfRecords><records><record><recordSchema>dc</recordSchema><recordData><dc xmlns:dc="http://purl.org/dc/elements/1.1/"><dc:title>T</dc:title><dc:identifier>ark:/12148/bpt6kX</dc:identifier></dc></recordData><recordPosition>1</recordPosition></record></records></searchRetrieveResponse>"""
    router.get("https://gallica.bnf.fr/services/engine/search/sru").mock(return_value=Response(200, text=xml))
    res = runner.invoke(cli, ["search", '--query', 'dc.title="Paris"', "--rows", "1", "--json"])
    assert res.exit_code == 0
    assert "ark:/12148" in res.output

def test_cli_manifest(router):
    runner = CliRunner()
    ark = "ark:/12148/bpt6k000001"
    url = f"https://gallica.bnf.fr/iiif/{ark}/manifest.json"
    router.get(url).mock(return_value=Response(200, json={"label": "Doc"}))
    res = runner.invoke(cli, ["manifest", ark])
    assert res.exit_code == 0
    assert "Doc" in res.output
