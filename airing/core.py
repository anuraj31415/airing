from datetime import datetime


def parse_shows(media):
    """Turn raw media dicts into flat dicts, skipping ones with no next episode."""
    shows = []
    for m in media:
        nxt = m.get("nextAiringEpisode")
        if not nxt or nxt.get("airingAt") is None:
            continue
        title = m.get("title") or {}
        romaji = title.get("romaji") or title.get("english")
        if not romaji:
            continue
        shows.append(
            {
                "romaji": romaji,
                "english": title.get("english") or None,
                "episode": nxt.get("episode"),
                "airing_at": int(nxt["airingAt"]),
            }
        )
    return shows


def in_window(shows, now, days):
    """Keep shows airing from now up to and including now + days. now is a unix timestamp."""
    end = now + days * 86400
    return [s for s in shows if now <= s["airing_at"] <= end]


def sort_shows(shows):
    return sorted(shows, key=lambda s: (s["airing_at"], s["romaji"]))


def select(media, now, days, limit=None):
    shows = sort_shows(in_window(parse_shows(media), now, days))
    if limit is not None:
        shows = shows[: max(limit, 0)]
    return shows


def countdown(airing_at, now):
    secs = int(airing_at - now)
    if secs <= 0:
        return "now"
    mins = secs // 60
    d, rem = divmod(mins, 1440)
    h, m = divmod(rem, 60)
    if d:
        return "in %dd %dh" % (d, h)
    if h:
        return "in %dh %dm" % (h, m)
    return "in %dm" % max(m, 1)


def local_time(airing_at):
    return datetime.fromtimestamp(airing_at).strftime("%a %H:%M")


def format_title(show):
    if show["english"] and show["english"] != show["romaji"]:
        return "%s (%s)" % (show["romaji"], show["english"])
    return show["romaji"]


def format_lines(shows, now):
    rows = [
        (format_title(s), "ep %s" % s["episode"], countdown(s["airing_at"], now), local_time(s["airing_at"]))
        for s in shows
    ]
    if not rows:
        return []
    w = max(len(r[0]) for r in rows)
    return ["%-*s  %-7s %-11s %s" % (w, *r) for r in rows]


def to_json_items(shows, now):
    return [
        {
            "romaji": s["romaji"],
            "english": s["english"],
            "episode": s["episode"],
            "airing_at": s["airing_at"],
            "airing_at_iso": datetime.fromtimestamp(s["airing_at"]).astimezone().isoformat(),
            "countdown": countdown(s["airing_at"], now),
        }
        for s in shows
    ]
