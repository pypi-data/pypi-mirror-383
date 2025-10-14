from bs4 import NavigableString


class LinkedText:
    def __init__(self, content):
        self.content = content

    def __eq__(self, other):
        return self.text == other.text and self.link == other.link

    def __hash__(self):
        return hash((self.text, self.link))

    def __repr__(self):
        return f"<LinkedText: {self.text} ({self.link})>"

    @property
    def link(self):
        if isinstance(self.content, NavigableString) or not self.content:
            return None
        return (self.content.a or self.content).get("href")

    @property
    def text(self):
        return self.content.text.strip()
