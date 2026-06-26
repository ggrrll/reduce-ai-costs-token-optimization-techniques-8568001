"""311 passing cases + 1 real failure (test_negative_charge). A genuine pytest run —
not a canned text file. Raw `pytest -q` is a wall of dots; `rtk test pytest -q` shows
only the failure."""
import pytest
from paykit import create_charge


@pytest.mark.parametrize("amount", range(1, 312))
def test_positive_charge(amount):
    result = create_charge(amount)
    assert result[0] == 201


def test_negative_charge():
    # bug-in-test: forgets create_charge(-100) raises PayError, so this fails for real
    result = create_charge(-100)
    assert result[0] == 201
