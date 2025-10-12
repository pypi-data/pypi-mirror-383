import textwrap

import requests
import readabilipy
import markdownify
from ddgs import DDGS

from .utils import MissingOrEmpty, UnsupportedMimeType, InvalidUrl, ResponseTooLong, RequestFailed


web_fetch_types = ['text/plain', 'text/html', 'application/json', 'application/xml', 'text/xml']
web_fetch_max_size = 10_000_000
web_fetch_max_text_length = 100_000


def web_search(query: str) -> str:
    if not query:
        raise MissingOrEmpty(name="query")

    results = DDGS().text(query, backend='duckduckgo', safesearch='off', max_results=10)

    return format_search_results(results)


def web_fetch(url: str) -> str:
    """
    Fetch web content from a URL.

    Arguments:
        url: the URL to fetch

    Returns a plain-text representation of the content, if possible.
    """
    try:
       with requests.get(url, stream=True) as r:
            content_type = r.headers.get('content-type', '').split(';')[0].strip()

            if content_type not in web_fetch_types:
                raise UnsupportedMimeType(type=content_type)

            total = 0
            data = bytearray()

            for chunk in r.iter_content(chunk_size=8192):
                total += len(chunk)
                if total > web_fetch_max_size:
                    raise ResponseTooLong(max=web_fetch_max_text_length)

                data.extend(chunk)

            text = data.decode(r.encoding or 'utf-8', errors="replace")

            if content_type == 'text/html':
                readable = readabilipy.simple_json_from_html_string(text, use_readability=True)
                text = markdownify.markdownify(readable['content'] or "", heading_style=markdownify.ATX)
            
            if len(text) > web_fetch_max_text_length:
                raise ResponseTooLong(max=web_fetch_max_text_length)

            return text

    except Exception as e:
        raise RequestFailed(error=str(e))


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


