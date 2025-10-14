from typing import ClassVar

from bs4 import BeautifulSoup


class Wikiobject:
    _html_tag: str | None = None
    _identifier: ClassVar[dict[str, str]] = {}

    def __init__(self, value):
        self.value = value

    def __new__(cls, *args, **kwargs):
        if cls == Wikiobject:
            raise NotImplementedError("Wikiobject should not be created directly")

        return super().__new__(cls)

    @classmethod
    def from_html(cls, html: str):
        soup = BeautifulSoup(html, "html.parser")
        return cls.from_soup(soup)

    @classmethod
    def from_soup(cls, soup: BeautifulSoup):
        return cls(soup.find(cls._html_tag, cls._identifier))

    @property
    def parent_heading(self):
        heading_div = self.value.find_previous_sibling("div")
        heading = (
            heading_div.find("h2")
            if heading_div
            else self.value.find_previous_sibling("h2")
        )
        return heading.text if heading else None
