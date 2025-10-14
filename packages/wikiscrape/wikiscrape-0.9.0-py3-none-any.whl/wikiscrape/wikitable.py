import re
import typing

from bs4 import BeautifulSoup

from .wikiobject import Wikiobject

FOOTNOTE = r"(\[)(\w+|\d+)(\])"
DAGGER = "\u2020"
DOUBLE_DAGGER = "\u2021"


def de_footnoted_soup(x: BeautifulSoup) -> BeautifulSoup:
    return BeautifulSoup(remove_footnotes(str(x)), "html.parser")


def remove_footnotes(text: str) -> str:
    return re.sub(
        FOOTNOTE, "", text.replace(DAGGER, "").replace(DOUBLE_DAGGER, "")
    ).strip()


class Wikitable(Wikiobject):
    _html_tag = "table"
    _identifier: typing.ClassVar[dict[str, str]] = {"class": "wikitable"}

    @classmethod
    def from_title(cls, title: str, html: str) -> "Wikitable":
        all_titles = BeautifulSoup(html, "html.parser").find_all("h2")
        tag = next(tag for tag in all_titles if tag.text == title)

        if not tag:
            raise ValueError(f"Title {tag} not found in html")

        parent_classes = tag.parent.get("class", [])
        sibling_object = tag.parent if "mw-heading" in parent_classes else tag
        table = sibling_object.find_next_sibling("table")
        return cls.from_html(str(table))

    @property
    def headers(self) -> list[str]:
        header_contents = [
            th.contents for row in self.header_rows for th in row.find_all("th")
        ]
        if not header_contents:
            return [f"col_{i+1}" for i in range(len(self.data[0]))]

        return [
            remove_footnotes(next((el.text.strip() for el in c if el.text.strip()), ""))
            for c in header_contents
        ]

    @property
    @typing.no_type_check
    def data(self) -> list[list[BeautifulSoup]]:
        return [
            [
                de_footnoted_soup(str(td.contents[0])).contents[0]
                if len(td.contents) == 1 and bool(str(td.contents[0]).strip())
                else de_footnoted_soup("".join(str(x) for x in td.contents))
                for td in tr.find_all("td")
            ]
            for tr in self.data_rows
        ]

    @property
    def data_rows(self) -> list[BeautifulSoup]:
        return [row for row in self.rows if not row.th]

    @property
    def header_rows(self) -> list[BeautifulSoup]:
        return [row for row in self.rows if row.th]

    @property
    def rows(self) -> list[BeautifulSoup]:
        return self.value.find_all("tr")

    def to_dicts(self) -> list[dict[str, BeautifulSoup]]:
        return [dict(zip(self.headers, row)) for row in self.data]
