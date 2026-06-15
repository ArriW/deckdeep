import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from deckdeep.events import DarkMerchant  # noqa: E402


def test_dark_merchant_description_is_well_formed():
    """Regression: the Dark Merchant event description must use the corrected,
    grammatical phrasing and never the old garbled text."""
    description = DarkMerchant().description

    # Corrected phrasing must be present.
    assert "appears and offers you" in description
    assert "Do you accept" in description

    # Old garbled fragments must never reappear.
    assert "appears offers" not in description
    assert "A Do you can accept" not in description
