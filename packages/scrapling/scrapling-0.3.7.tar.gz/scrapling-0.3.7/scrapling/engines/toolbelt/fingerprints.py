"""
Functions related to generating headers and fingerprints generally
"""

from functools import lru_cache
from platform import system as platform_system

from tldextract import extract
from browserforge.headers import Browser, HeaderGenerator

from scrapling.core._types import Dict, Literal

__OS_NAME__ = platform_system()
OSName = Literal["linux", "macos", "windows"]


@lru_cache(10, typed=True)
def generate_convincing_referer(url: str) -> str:
    """Takes the domain from the URL without the subdomain/suffix and make it look like you were searching Google for this website

    >>> generate_convincing_referer('https://www.somewebsite.com/blah')
    'https://www.google.com/search?q=somewebsite'

    :param url: The URL you are about to fetch.
    :return: Google's search URL of the domain name
    """
    website_name = extract(url).domain
    return f"https://www.google.com/search?q={website_name}"


@lru_cache(1, typed=True)
def get_os_name() -> OSName | None:
    """Get the current OS name in the same format needed for browserforge, if the OS is Unknown, return None so browserforge uses all.

    :return: Current OS name or `None` otherwise
    """
    match __OS_NAME__:
        case "Linux":
            return "linux"
        case "Darwin":
            return "macos"
        case "Windows":
            return "windows"
        case _:
            return None


def generate_headers(browser_mode: bool = False) -> Dict:
    """Generate real browser-like headers using browserforge's generator

    :param browser_mode: If enabled, the headers created are used for playwright, so it has to match everything
    :return: A dictionary of the generated headers
    """
    # In the browser mode, we don't care about anything other than matching the OS and the browser type with the browser we are using,
    # So we don't raise any inconsistency red flags while websites fingerprinting us
    os_name = get_os_name()
    browsers = [Browser(name="chrome", min_version=130)]
    if not browser_mode:
        os_name = ("windows", "macos", "linux")
        browsers.extend(
            [
                Browser(name="firefox", min_version=130),
                Browser(name="edge", min_version=130),
            ]
        )
    if os_name:
        return HeaderGenerator(browser=browsers, os=os_name, device="desktop").generate()
    else:
        return HeaderGenerator(browser=browsers, device="desktop").generate()


__default_useragent__ = generate_headers(browser_mode=False).get("User-Agent")
