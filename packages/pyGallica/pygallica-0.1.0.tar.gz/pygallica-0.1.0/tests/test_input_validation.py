import pytest
from pyGallica.client import validate_ark

@pytest.mark.parametrize("ark", [
    "ark:/12148/bpt6k123456",
    "ark:/12148/btv1b12345",
])
def test_valid_arks(ark):
    assert validate_ark(ark)

@pytest.mark.parametrize("ark", ["", "ark:////", "foo", "ark:/wrong/format"])
def test_invalid_arks(ark):
    with pytest.raises(ValueError):
        validate_ark(ark)
