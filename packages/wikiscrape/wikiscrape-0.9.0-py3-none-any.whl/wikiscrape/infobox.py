from typing import ClassVar

from bs4 import BeautifulSoup

from .wikitable import Wikitable


class Infobox(Wikitable):
    _identifier: ClassVar[dict] = {"class": "infobox"}

    @property
    def data(self) -> list[list[BeautifulSoup]]:
        extract_value = (
            lambda tr: tr.td.contents[0]
            if len(tr.td.contents) == 1
            else BeautifulSoup("".join(str(x) for x in tr.td.contents), "html.parser")
        )
        get_next_row_value = (
            lambda i: extract_value(self.rows[i + 1])
            if i + 1 < len(self.rows)
            and self.rows[i + 1].td
            and not self.rows[i + 1].th
            else None
        )

        return [
            [
                extract_value(tr) if tr.td else get_next_row_value(i)
                for i, tr in enumerate(self.rows)
                if tr.th
            ]
        ]
