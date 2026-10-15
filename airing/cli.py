import argparse
import json
import sys
import time

from . import api, core


def build_parser():
    p = argparse.ArgumentParser(prog="airing", description="Anime airing in the next N days, from AniList.")
    p.add_argument("--days", type=int, default=7, help="window width in days (default 7)")
    p.add_argument("--limit", type=int, default=None, help="show at most N shows")
    p.add_argument("--json", action="store_true", help="print JSON instead of text")
    return p


def main(argv=None, fetch=None, now=None):
    args = build_parser().parse_args(argv)
    if args.days < 1:
        print("airing: --days must be at least 1", file=sys.stderr)
        return 2
    if args.limit is not None and args.limit < 1:
        print("airing: --limit must be at least 1", file=sys.stderr)
        return 2
    fetch = fetch or api.fetch_media
    now = int(time.time()) if now is None else now
    try:
        media = fetch()
    except api.ApiError as e:
        print("airing: %s" % e, file=sys.stderr)
        return 1
    shows = core.select(media, now, args.days, args.limit)
    if args.json:
        print(json.dumps(core.to_json_items(shows, now), indent=2, ensure_ascii=False))
    elif not shows:
        print("nothing airing in the next %d days" % args.days)
    else:
        print("\n".join(core.format_lines(shows, now)))
    return 0


def run():
    sys.exit(main())


if __name__ == "__main__":
    run()
