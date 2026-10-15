import json
import urllib.error
import urllib.request

URL = "https://graphql.anilist.co"
TIMEOUT = 10

QUERY = """
query {
  Page(perPage: 50) {
    media(type: ANIME, status: RELEASING, sort: POPULARITY_DESC) {
      title { romaji english }
      nextAiringEpisode { episode airingAt }
    }
  }
}
"""


class ApiError(Exception):
    pass


def fetch_media(url=URL, timeout=TIMEOUT):
    """POST the query once and return the list of media dicts."""
    body = json.dumps({"query": QUERY}).encode()
    req = urllib.request.Request(
        url,
        data=body,
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "airing-cli",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            payload = json.load(resp)
    except urllib.error.HTTPError as e:
        raise ApiError("AniList returned HTTP %d" % e.code)
    except urllib.error.URLError as e:
        raise ApiError("can't reach AniList: %s" % e.reason)
    except (OSError, ValueError) as e:
        raise ApiError("bad response from AniList: %s" % e)
    return parse_response(payload)


def parse_response(payload):
    if not isinstance(payload, dict):
        raise ApiError("unexpected response from AniList")
    if payload.get("errors"):
        msg = payload["errors"][0].get("message", "unknown error")
        raise ApiError("AniList error: %s" % msg)
    try:
        return payload["data"]["Page"]["media"] or []
    except (KeyError, TypeError):
        raise ApiError("unexpected response shape from AniList")
