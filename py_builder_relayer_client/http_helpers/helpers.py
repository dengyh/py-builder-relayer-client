import os
import requests

from ..exceptions import RelayerApiException

GET = "GET"
POST = "POST"
DELETE = "DELETE"
PUT = "PUT"


def _get_proxy_config():
    """
    Get proxy configuration from PROXY_URL environment variable
    Returns a dict suitable for requests library proxies parameter

    Supports HTTP, HTTPS, and SOCKS5 proxy protocols:
    - HTTP: http://proxy:port
    - HTTPS: https://proxy:port
    - SOCKS5: socks5://proxy:port or socks5h://proxy:port
    """
    proxy_url = os.getenv("PROXY_URL")
    if not proxy_url:
        return None

    # requests library expects proxies in format:
    # {'http': 'http://proxy:port', 'https': 'https://proxy:port'}
    # If PROXY_URL is provided, use it for both http and https
    # SOCKS5 URLs (socks5:// or socks5h://) are also supported
    return {
        'http': proxy_url,
        'https': proxy_url,
    }


def request(endpoint: str, method: str, headers=None, data=None):
    try:
        proxies = _get_proxy_config()
        resp = requests.request(
            method=method,
            url=endpoint,
            headers=headers,
            json=data if data else None,
            proxies=proxies,
        )
        if resp.status_code != 200:
            raise RelayerApiException(resp)

        try:
            return resp.json()
        except requests.JSONDecodeError:
            return resp.text

    except requests.RequestException:
        raise RelayerApiException(error_msg="Request exception!")


def post(endpoint, headers=None, data=None):
    return request(endpoint, POST, headers, data)


def get(endpoint, headers=None, data=None):
    return request(endpoint, GET, headers, data)


def delete(endpoint, headers=None, data=None):
    return request(endpoint, DELETE, headers, data)
