from http.cookies import SimpleCookie
from typing import Any

import scrapy
from fake_useragent import UserAgent


def get_default_headers(**kwargs: Any) -> dict[str, str]:
    if not kwargs:
        kwargs = dict(platforms=["desktop"])
    user_agent = UserAgent(**kwargs)

    headers = {
        "User-Agent": user_agent.random
    }
    return headers


def update_headers(
        headers: dict[str, str] | None = None,
        default_headers: dict[str, str] | None = None
) -> dict[str, str]:
    if headers is None:
        headers = {}
    if default_headers is None:
        default_headers = get_default_headers()

    for k, v in default_headers.items():
        if k not in headers:
            headers[k] = v

    return headers


def scrapy_response_headers_to_cookies(response: scrapy.http.Response) -> dict[str, str]:
    cookies = {}
    for header in response.headers.getlist("Set-Cookie"):
        c = SimpleCookie()
        c.load(header.decode())
        for key, morsel in c.items():
            cookies[key] = morsel.value
    return cookies


if __name__ == '__main__':
    print(get_default_headers())
    print(update_headers({"a": "1"}, {"b": "2"}))
