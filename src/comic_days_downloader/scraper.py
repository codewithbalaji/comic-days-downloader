import json

import requests
from bs4 import BeautifulSoup

USER_AGENT = (
    "Mozilla/5.0 "
    "(Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 "
    "(KHTML, like Gecko) "
    "Chrome/140.0.0.0 Safari/537.36"
)


def fetch_episode_pages(url: str) -> dict[int, dict]:
    """Fetch a comic-days.com episode page and return its pages, numbered from 1.

    Returns a dict mapping page number -> page image metadata (src, width, height),
    ordered the same way the site itself orders them (sorted by image src).
    """

    session = requests.Session()

    session.headers.update({
        "User-Agent": USER_AGENT,
        "Accept": (
            "text/html,application/xhtml+xml,"
            "application/xml;q=0.9,image/avif,"
            "image/webp,*/*;q=0.8"
        ),
        "Accept-Language": "en-US,en;q=0.9",
    })

    response = session.get(url, timeout=30)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    episode_json = soup.find(id="episode-json")

    if episode_json is None:
        raise RuntimeError("Could not find #episode-json in the page.")

    # Comic Days stores the JSON in a `data-value` attribute, not `value`.
    json_string = episode_json.get("data-value")

    if not json_string:
        raise RuntimeError("episode-json does not contain a 'data-value' attribute.")

    try:
        dynamic_json = json.loads(json_string)
    except json.JSONDecodeError as error:
        raise RuntimeError(f"Could not parse episode JSON: {error}") from error

    try:
        pages = dynamic_json["readableProduct"]["pageStructure"]["pages"]
    except KeyError as error:
        raise RuntimeError(f"Expected JSON property was not found: {error}") from error

    pages = [
        page
        for page in pages
        if page.get("src") and str(page.get("src")).strip()
    ]

    pages.sort(key=lambda page: page["src"])

    return {index + 1: page for index, page in enumerate(pages)}
