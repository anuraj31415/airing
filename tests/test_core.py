import json
from pathlib import Path

import pytest

from airing import api, core

NOW = 1000000000
DAY = 86400
SAMPLE = json.loads((Path(__file__).parent / "fixtures" / "sample.json").read_text())


def media():
    return api.parse_response(SAMPLE)


def show(airing_at, romaji="X", english=None, episode=1):
    return {"romaji": romaji, "english": english, "episode": episode, "airing_at": airing_at}


def test_empty_results():
    assert core.select([], NOW, 7) == []
    assert core.format_lines([], NOW) == []
    assert api.parse_response({"data": {"Page": {"media": []}}}) == []


def test_no_english_title():
    shows = core.parse_shows(media())
    s = next(x for x in shows if x["romaji"] == "No English Show")
    assert s["english"] is None
    assert core.format_title(s) == "No English Show"


def test_english_title_shown():
    assert core.format_title(show(0, "Soon Show", "Soon English")) == "Soon Show (Soon English)"


def test_skips_shows_without_next_episode():
    names = [s["romaji"] for s in core.parse_shows(media())]
    assert "Finished Show" not in names


def test_window_boundary():
    end = NOW + 7 * DAY
    shows = [show(end, "edge"), show(end + 1, "outside"), show(end - 1, "inside"), show(NOW - 1, "past")]
    got = [s["romaji"] for s in core.in_window(shows, NOW, 7)]
    assert sorted(got) == ["edge", "inside"]


def test_days_widens_and_narrows():
    m = media()
    assert len(core.select(m, NOW, 1)) == 1
    assert len(core.select(m, NOW, 7)) == 3


def test_sorted_soonest_first():
    got = [s["romaji"] for s in core.select(media(), NOW, 7)]
    assert got == ["Soon Show", "No English Show", "Late Show"]


def test_limit():
    got = core.select(media(), NOW, 7, limit=2)
    assert [s["romaji"] for s in got] == ["Soon Show", "No English Show"]


@pytest.mark.parametrize(
    "secs,expected",
    [
        (0, "now"),
        (-5, "now"),
        (20, "in 1m"),
        (59 * 60, "in 59m"),
        (3600, "in 1h 0m"),
        (5 * 3600 + 30 * 60, "in 5h 30m"),
        (2 * DAY + 4 * 3600, "in 2d 4h"),
        (7 * DAY, "in 7d 0h"),
    ],
)
def test_countdown(secs, expected):
    assert core.countdown(NOW + secs, NOW) == expected


def test_format_lines_contains_episode_and_countdown():
    lines = core.format_lines([show(NOW + 2 * DAY + 4 * 3600, "A", episode=7)], NOW)
    assert len(lines) == 1
    assert "ep 7" in lines[0] and "in 2d 4h" in lines[0]


def test_graphql_error():
    with pytest.raises(api.ApiError, match="boom"):
        api.parse_response({"errors": [{"message": "boom"}]})


def test_bad_shape():
    with pytest.raises(api.ApiError):
        api.parse_response({"data": None})
