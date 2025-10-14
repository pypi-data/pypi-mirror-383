class Markdown:
    @staticmethod
    def a(page: str, alias: str | None = None) -> str:
        return f"[[{page}|{alias}]]" if alias else f"[[{page}]]"

    @staticmethod
    def b(text: str) -> str:
        return f"'''{text}'''"

    @staticmethod
    def em(text: str) -> str:
        return f"''{text}''"

    @staticmethod
    def h(level: int, text: str) -> str:
        return f"{'=' * (level+1)}{text}{'=' * (level+1)}"

    @staticmethod
    def ul(items: list[str]) -> str:
        return "\n".join([f"* {item}" for item in items])

    @staticmethod
    def br() -> str:
        return "<br/>"

    @staticmethod
    def hr() -> str:
        return "\n----\n"

    @staticmethod
    def comment(text: str) -> str:
        return f"<!-- {text} -->"

    @staticmethod
    def template(content: str) -> str:
        return f"{'{{'}{content}{'}}'}"
