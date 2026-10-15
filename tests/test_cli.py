import json
from pathlib import Path

from airing import api, cli

NOW = 1000000000
SAMPLE = json.loads((Path(__file__).parent / "fixtures" / "sample.json").read_text())


def fetch():
    return api.parse_response(SAMPLE)


def test_text_output(capsys):
    assert cli.main([], fetch=fetch, now=NOW) == 0
    lines = capsys.readouterr().out.splitlines()
    assert len(lines) == 3
    assert lines[0].startswith("Soon Show (Soon English)")


def test_json_output(capsys):
    assert cli.main(["--json", "--limit", "1"], fetch=fetch, now=NOW) == 0
    data = json.loads(capsys.readouterr().out)
    assert len(data) == 1
    assert data[0]["romaji"] == "Soon Show"
    assert data[0]["episode"] == 12


def test_empty_message(capsys):
    assert cli.main([], fetch=lambda: [], now=NOW) == 0
    assert "nothing airing" in capsys.readouterr().out


def test_api_error_exits_nonzero(capsys):
    def boom():
        raise api.ApiError("can't reach AniList: down")

    assert cli.main([], fetch=boom, now=NOW) == 1
    assert "can't reach AniList" in capsys.readouterr().err


def test_bad_days(capsys):
    assert cli.main(["--days", "0"], fetch=fetch, now=NOW) == 2
