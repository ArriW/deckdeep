import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from deckdeep.relic import Relic  # noqa: E402
from deckdeep.text_utils import truncate_name, wrap_name  # noqa: E402


_ELLIPSIS = "\u2026"


def test_truncate_name_short_unchanged():
    assert truncate_name("Hair of the Dog", 18) == "Hair of the Dog"
    assert truncate_name("Cursed Coin", 12) == "Cursed Coin"


def test_truncate_name_long_gets_ellipsis_within_max_len():
    out = truncate_name("Equivalent Exchange", 18)
    assert out == "Equivalent Exchan" + _ELLIPSIS
    assert len(out) == 18
    assert out.endswith(_ELLIPSIS)


def test_truncate_name_strips_trailing_whitespace_before_ellipsis():
    name = "abc   " + "defghijklmnopqrstuvwxyz"
    out = truncate_name(name, 12)
    assert out.endswith(_ELLIPSIS)
    assert len(out) <= 12
    assert not out[:-1].endswith(" ")


def test_truncate_name_max_len_one_returns_ellipsis():
    assert truncate_name("anything", 1) == _ELLIPSIS


def test_truncate_name_max_len_zero_returns_ellipsis():
    assert truncate_name("anything", 0) == _ELLIPSIS
    assert truncate_name("anything", -5) == _ELLIPSIS


def test_truncate_name_exact_length_unchanged():
    name = "abcdefghij"  # 10 chars
    assert truncate_name(name, 10) == name


def test_relic_display_name_caps_long_name_with_ellipsis():
    relic = Relic(
        "Equivalent Exchange",
        {
            "description": "Test relic.",
            "effect": lambda p, g: None,
            "trigger_when": 0,
        },
    )
    assert relic.display_name == "Equivalent Exchan" + _ELLIPSIS
    assert len(relic.display_name) == 18
    assert relic.display_name.endswith(_ELLIPSIS)


def test_relic_display_name_short_name_unchanged():
    relic = Relic(
        "Cursed Coin",
        {
            "description": "Test relic.",
            "effect": lambda p, g: None,
            "trigger_when": 0,
        },
    )
    assert relic.display_name == "Cursed Coin"


def test_wrap_name_empty_returns_empty_list():
    assert wrap_name("", 10) == []
    assert wrap_name("   ", 10) == []
    assert wrap_name("\t\n  ", 10) == []


def test_wrap_name_collapses_whitespace():
    assert wrap_name("hello   world", 20) == ["hello world"]


def test_wrap_name_greedy_word_wrap():
    assert wrap_name("a very long string indeed", 10) == [
        "a very",
        "long",
        "string",
        "indeed",
    ]


def test_wrap_name_hard_splits_overwidth_words():
    result = wrap_name("supercalifragilistic", 5)
    assert result == ["super", "calif", "ragil", "istic"]
    assert all(len(line) <= 5 for line in result)


def test_wrap_name_mix_short_and_overwidth_words():
    result = wrap_name("hi supercalifragilistic bye", 5)
    assert result == ["hi", "super", "calif", "ragil", "istic", "bye"]
    assert all(len(line) <= 5 for line in result)


def test_wrap_name_fits_exactly():
    assert wrap_name("hello world", 11) == ["hello world"]


def test_wrap_name_each_line_respects_max_width():
    text = "the quick brown fox jumps over the lazy dog"
    for width in (5, 8, 12, 20):
        for line in wrap_name(text, width):
            assert len(line) <= width
