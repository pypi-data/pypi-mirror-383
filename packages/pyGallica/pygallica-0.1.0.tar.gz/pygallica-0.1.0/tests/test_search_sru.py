from pyGallica.client import GallicaClient
import pytest

def test_client_defaults():
    c = GallicaClient()
    assert c.base_url.startswith("https://")
    assert c.timeout > 0

def test_client_invalid_timeout():
    with pytest.raises(ValueError):
        GallicaClient(timeout=0)

def test_user_agent_settable():
    c = GallicaClient(user_agent="pyllica/0.1")
    assert "pyllica/0.1" in c._headers()["User-Agent"]
