# airing

Shows which anime are airing soon and how long until the next episode. It asks AniList for the 50 most popular releasing shows, keeps the ones airing in the next 7 days, and sorts them soonest first.

The window is the next N days from now, not the calendar week. Default is 7.

## Install

Needs Python 3.9 or newer. No dependencies.

    git clone https://github.com/anuraj31415/airing.git
    cd airing
    pip install .

## Usage

    $ airing --limit 3
    Sample Show One (Sample One)  ep 5    in 3h 10m   Wed 12:26
    Another Sample                ep 12   in 1d 4h    Thu 13:16
    Third Sample (Third)          ep 3    in 5d 2h    Mon 11:16

The titles above are made up, the layout is real. Columns are title (romaji, then English if there is one), next episode, countdown, and local air time.

## Flags

- `--days N` window width in days, default 7
- `--limit N` show at most N shows
- `--json` print JSON instead of text

If AniList can't be reached or returns an error, it prints a message to stderr and exits 1. Requests time out after 10 seconds.

## Notes

Uses AniList's public GraphQL API at https://graphql.anilist.co, one request per run. Because it only looks at the top 50 by popularity, smaller shows can be missing.

Tests: `pip install -e ".[test]"` then `pytest`. They don't touch the network.
