from itertools import chain, islice, tee

from bs4 import BeautifulSoup
from docutils.core import publish_string
from markdown import markdown


def truncate_words(s: str, limit: int) -> str:
    if len(s) <= limit:
        return s
    # find last space before or at limit
    cut = s.rfind(" ", 0, limit)
    if cut == -1:  # no space found, just hard cut
        return s[:limit]
    if cut == len(s):
        return s
    return s[:cut] + "..."


def get_text(content: str) -> str:
    soup = BeautifulSoup(content, "html.parser")
    return soup.get_text()


def get_excerpt(text: str, limit: int = 300) -> str:
    return truncate_words(text, limit=limit)


def prev_current_next(iterable):
    a, b, c = tee(iterable, 3)
    prevs = chain([None], a)
    items = b
    nexts = chain(islice(c, 1, None), [None])
    return zip(prevs, items, nexts)


def markdown_to_html(content: str) -> str:
    return markdown(content, extensions=["fenced_code", "codehilite", "tables"])


def rst_to_html(content: str) -> str:
    return publish_string(content, writer_name="html").decode("utf-8")
