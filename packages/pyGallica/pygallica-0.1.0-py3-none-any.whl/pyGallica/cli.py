import json
import click
from .client import GallicaClient

@click.group()
def cli():
    pass

@cli.command()
@click.option("--query", required=True)
@click.option("--rows", default=10, type=int)
@click.option("--json", "as_json", is_flag=True, default=False)
def search(query, rows, as_json):
    c = GallicaClient()
    res = c.search_sru(query, rows=rows)
    out = [{"ark": r.ark, "title": r.title} for r in res.records]
    if as_json:
        click.echo(json.dumps(out, ensure_ascii=False))
    else:
        for r in out:
            click.echo(f"{r['ark']} | {r['title']}")

@cli.command()
@click.argument("ark")
def manifest(ark):
    c = GallicaClient()
    m = c.get_manifest(ark)
    click.echo(m.get("label", ""))
