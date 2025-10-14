from .wikiobject import Wikiobject


class Header(Wikiobject):
    _html_tag = "h2"

    @property
    def text(self) -> str:
        return self.value.text
