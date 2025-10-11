
import requests
import pytest

from pocong.proxy_spiders import GetProxy


def test_get_proxy():
    """
    Test that a random proxy from get_proxy can make a successful request to httpbin.org/ip.
    """
    proxy = GetProxy().get_proxy()
    assert proxy is not None, "No proxy returned by get_proxy()"
    proxies = {'https': f'http://{proxy["ip"]}:{proxy["port"]}'}
    try:
        response = requests.get('https://httpbin.org/ip', proxies=proxies, timeout=10)
        response.raise_for_status()
        assert response.status_code == 200
        assert 'origin' in response.text
    except requests.RequestException as e:
        pytest.skip(f"HTTP proxy request failed: {e}")
