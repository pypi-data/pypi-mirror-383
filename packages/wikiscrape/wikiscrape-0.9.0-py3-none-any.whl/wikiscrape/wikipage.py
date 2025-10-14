import requests
from bs4 import BeautifulSoup

from .markdown import Markdown as md  # noqa: N813


class Wikipage:
    def __init__(self, title: str):
        self.title = title

    def __eq__(self, other):
        return self.title == other.title

    def __hash__(self):
        return hash(self.title)

    @classmethod
    def from_url(cls, url: str):
        return cls(url.split("/")[-1].replace("_", " ").replace("%27", "'"))

    @property
    def abs_url(self) -> str:
        EN_WIKI = "https://en.wikipedia.org/wiki/"  # noqa: N806
        return EN_WIKI + self.rel_url

    @property
    def rel_url(self) -> str:
        return self.title.replace(" ", "_").replace("'", "%27")

    @property
    def exists(self) -> bool:
        return bool(self.title) and not self.is_redlink

    @property
    def is_disambiguated(self) -> bool:
        return self.exists and "(" in self.title

    @property
    def is_redlink(self) -> bool:
        return "not exist" in self.title

    @property
    def soup(self) -> BeautifulSoup:
        return BeautifulSoup(self.text, "html.parser")

    @property
    def subject(self) -> str:
        return self.title.split(" (")[0]

    @property
    def text(self) -> str:
        return requests.get(self.abs_url).text

    def to_link(self, alias: str | None = None) -> str:
        return md.a(self.title) if not alias else md.a(self.title, alias)
