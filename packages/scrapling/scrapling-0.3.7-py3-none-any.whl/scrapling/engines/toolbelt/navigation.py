"""
Functions related to files and URLs
"""

from pathlib import Path
from functools import lru_cache
from urllib.parse import urlparse

from playwright.async_api import Route as async_Route
from msgspec import Struct, structs, convert, ValidationError
from playwright.sync_api import Route

from scrapling.core.utils import log
from scrapling.core._types import Dict, Tuple, overload, Literal
from scrapling.engines.constants import DEFAULT_DISABLED_RESOURCES

__BYPASSES_DIR__ = Path(__file__).parent / "bypasses"


class ProxyDict(Struct):
    server: str
    username: str = ""
    password: str = ""


def intercept_route(route: Route):
    """This is just a route handler, but it drops requests that its type falls in `DEFAULT_DISABLED_RESOURCES`

    :param route: PlayWright `Route` object of the current page
    :return: PlayWright `Route` object
    """
    if route.request.resource_type in DEFAULT_DISABLED_RESOURCES:
        log.debug(f'Blocking background resource "{route.request.url}" of type "{route.request.resource_type}"')
        route.abort()
    else:
        route.continue_()


async def async_intercept_route(route: async_Route):
    """This is just a route handler, but it drops requests that its type falls in `DEFAULT_DISABLED_RESOURCES`

    :param route: PlayWright `Route` object of the current page
    :return: PlayWright `Route` object
    """
    if route.request.resource_type in DEFAULT_DISABLED_RESOURCES:
        log.debug(f'Blocking background resource "{route.request.url}" of type "{route.request.resource_type}"')
        await route.abort()
    else:
        await route.continue_()


@overload
def construct_proxy_dict(proxy_string: str | Dict[str, str] | Tuple, as_tuple: Literal[True]) -> Tuple: ...


@overload
def construct_proxy_dict(proxy_string: str | Dict[str, str] | Tuple, as_tuple: Literal[False] = False) -> Dict: ...


def construct_proxy_dict(proxy_string: str | Dict[str, str] | Tuple, as_tuple: bool = False) -> Dict | Tuple:
    """Validate a proxy and return it in the acceptable format for Playwright
    Reference: https://playwright.dev/python/docs/network#http-proxy

    :param proxy_string: A string or a dictionary representation of the proxy.
    :param as_tuple: Return the proxy dictionary as a tuple to be cachable
    :return:
    """
    if isinstance(proxy_string, str):
        proxy = urlparse(proxy_string)
        if proxy.scheme not in ("http", "https", "socks4", "socks5") or not proxy.hostname:
            raise ValueError("Invalid proxy string!")

        try:
            result = {
                "server": f"{proxy.scheme}://{proxy.hostname}",
                "username": proxy.username or "",
                "password": proxy.password or "",
            }
            if proxy.port:
                result["server"] += f":{proxy.port}"
            return tuple(result.items()) if as_tuple else result
        except ValueError:
            # Urllib will say that one of the parameters above can't be casted to the correct type like `int` for port etc...
            raise ValueError("The proxy argument's string is in invalid format!")

    elif isinstance(proxy_string, dict):
        try:
            validated = convert(proxy_string, ProxyDict)
            result_dict = structs.asdict(validated)
            return tuple(result_dict.items()) if as_tuple else result_dict
        except ValidationError as e:
            raise TypeError(f"Invalid proxy dictionary: {e}")

    raise TypeError(f"Invalid proxy string: {proxy_string}")


@lru_cache(10, typed=True)
def js_bypass_path(filename: str) -> str:
    """Takes the base filename of a JS file inside the `bypasses` folder, then return the full path of it

    :param filename: The base filename of the JS file.
    :return: The full path of the JS file.
    """
    return str(__BYPASSES_DIR__ / filename)
