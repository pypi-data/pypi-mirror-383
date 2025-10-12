import textwrap
from ddgs import DDGS

from .utils import MissingOrEmpty


def web_search(query: str) -> str:
    if not query:
        raise MissingOrEmpty(name="query")

    results = DDGS().text(query, backend='duckduckgo', safesearch='off', max_results=10)

    return format_search_results(results)


def format_search_results(results: list[dict]) -> str:
    if not results:
        return "No results found."

    template = textwrap.dedent("""
        index: {number}
        title: {title}
        url: {href}
        snippet: {body}
    """).strip()

    results_formatted = [
        template.format(
            number=i,
            title=result.get("title", "No title"),
            href=result.get("href", "No URL"),
            body=result.get("body", "No description available"),
        )
        for i, result in enumerate(results)
    ]

    return "\n\n".join(results_formatted)


