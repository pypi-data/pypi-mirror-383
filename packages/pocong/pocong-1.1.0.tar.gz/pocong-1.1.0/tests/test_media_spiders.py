"""Tests for media_spiders module."""

from unittest.mock import Mock, patch

import pytest

from pocong.media_spiders import DynamicScrapingNews


class TestDynamicScrapingNews:
    """Test cases for DynamicScrapingNews class."""

    def test_init_without_proxy(self):
        """Test initialization without proxy."""
        scraper = DynamicScrapingNews("https://example.com", use_proxy=False)
        assert scraper.url == "https://example.com"
        assert scraper.use_proxy is False
        assert scraper.proxy is None

    def test_init_with_manual_proxy_string_ip_port(self):
        """Test initialization with manual proxy in ip:port format."""
        scraper = DynamicScrapingNews("https://example.com", manual_proxy="192.168.1.1:8080")
        assert scraper.url == "https://example.com"
        assert scraper.proxy == "http://192.168.1.1:8080"

    def test_init_with_manual_proxy_string_http(self):
        """Test initialization with manual proxy in http format."""
        scraper = DynamicScrapingNews("https://example.com", manual_proxy="http://192.168.1.1:8080")
        assert scraper.url == "https://example.com"
        assert scraper.proxy == "http://192.168.1.1:8080"

    def test_init_with_manual_proxy_string_https(self):
        """Test initialization with manual proxy in https format."""
        scraper = DynamicScrapingNews("https://example.com", manual_proxy="https://192.168.1.1:8080")
        assert scraper.url == "https://example.com"
        assert scraper.proxy == "https://192.168.1.1:8080"

    def test_init_with_manual_proxy_dict(self):
        """Test initialization with manual proxy as dictionary."""
        proxy_dict = {"ip": "192.168.1.1", "port": "8080"}
        scraper = DynamicScrapingNews("https://example.com", manual_proxy=proxy_dict)
        assert scraper.url == "https://example.com"
        assert scraper.proxy == "http://192.168.1.1:8080"

    def test_format_proxy_string_ip_port(self):
        """Test _format_proxy with ip:port string."""
        scraper = DynamicScrapingNews("https://example.com", use_proxy=False)
        result = scraper._format_proxy("192.168.1.1:8080")
        assert result == "http://192.168.1.1:8080"

    def test_format_proxy_string_http(self):
        """Test _format_proxy with http string."""
        scraper = DynamicScrapingNews("https://example.com", use_proxy=False)
        result = scraper._format_proxy("http://192.168.1.1:8080")
        assert result == "http://192.168.1.1:8080"

    def test_format_proxy_string_https(self):
        """Test _format_proxy with https string."""
        scraper = DynamicScrapingNews("https://example.com", use_proxy=False)
        result = scraper._format_proxy("https://192.168.1.1:8080")
        assert result == "https://192.168.1.1:8080"

    def test_format_proxy_dict_valid(self):
        """Test _format_proxy with valid dictionary."""
        scraper = DynamicScrapingNews("https://example.com", use_proxy=False)
        proxy_dict = {"ip": "192.168.1.1", "port": "8080"}
        result = scraper._format_proxy(proxy_dict)
        assert result == "http://192.168.1.1:8080"

    def test_format_proxy_dict_invalid(self):
        """Test _format_proxy with invalid dictionary."""
        scraper = DynamicScrapingNews("https://example.com", use_proxy=False)
        proxy_dict = {"host": "192.168.1.1", "port": "8080"}  # Missing 'ip' key

        with pytest.raises(ValueError) as exc_info:
            scraper._format_proxy(proxy_dict)
        assert "Manual proxy dict must contain 'ip' and 'port' keys" in str(exc_info.value)

    def test_format_proxy_invalid_type(self):
        """Test _format_proxy with invalid type."""
        scraper = DynamicScrapingNews("https://example.com", use_proxy=False)

        with pytest.raises(ValueError) as exc_info:
            scraper._format_proxy(123)  # Invalid type
        assert "Manual proxy must be a string or dict" in str(exc_info.value)

    def test_manual_proxy_overrides_use_proxy_false(self):
        """Test that manual proxy works even when use_proxy=False."""
        scraper = DynamicScrapingNews(
            "https://example.com",
            use_proxy=False,
            manual_proxy="192.168.1.1:8080"
        )
        assert scraper.proxy == "http://192.168.1.1:8080"

    @patch('pocong.media_spiders.GetProxy')
    @patch('pocong.media_spiders.PROXY_AVAILABLE', True)
    def test_manual_proxy_overrides_automatic_proxy(self, mock_get_proxy):
        """Test that manual proxy takes priority over automatic proxy."""
        # Setup mock for automatic proxy
        mock_proxy_getter = Mock()
        mock_proxy_getter.get_proxy_random.return_value = {"ip": "10.0.0.1", "port": "3128"}
        mock_get_proxy.return_value = mock_proxy_getter

        scraper = DynamicScrapingNews(
            "https://example.com",
            use_proxy=True,
            manual_proxy="192.168.1.1:8080"
        )

        # Manual proxy should be used, not automatic
        assert scraper.proxy == "http://192.168.1.1:8080"
        # Automatic proxy getter should not be called
        mock_get_proxy.assert_not_called()

    @patch('pocong.media_spiders.mechanize.Browser')
    @patch('pocong.media_spiders.UserAgent')
    def test_get_html_with_manual_proxy_mechanize_success(self, mock_ua, mock_browser_class):
        """Test _get_html with manual proxy using mechanize successfully."""
        # Setup mocks
        mock_ua_instance = Mock()
        mock_ua_instance.random = "Mozilla/5.0 Test"
        mock_ua.return_value = mock_ua_instance

        mock_browser = Mock()
        mock_browser.open.return_value.read.return_value.decode.return_value = "<html>Test</html>"
        mock_browser_class.return_value = mock_browser

        # Create scraper with manual proxy
        scraper = DynamicScrapingNews("https://example.com", manual_proxy="192.168.1.1:8080")

        # Test _get_html
        result = scraper._get_html("https://test.com")

        # Verify results
        assert result == "<html>Test</html>"
        mock_browser.set_proxies.assert_called_once_with({
            'http': 'http://192.168.1.1:8080',
            'https': 'http://192.168.1.1:8080'
        })
        mock_browser.open.assert_called_once_with("https://test.com")

    @patch('pocong.media_spiders.requests.get')
    @patch('pocong.media_spiders.mechanize.Browser')
    @patch('pocong.media_spiders.UserAgent')
    def test_get_html_with_manual_proxy_requests_fallback(self, mock_ua, mock_browser_class, mock_requests_get):
        """Test _get_html falls back to requests with proxy when mechanize fails."""
        # Setup mocks
        mock_ua_instance = Mock()
        mock_ua_instance.random = "Mozilla/5.0 Test"
        mock_ua.return_value = mock_ua_instance

        # Make mechanize fail
        mock_browser = Mock()
        mock_browser.open.side_effect = Exception("Mechanize failed")
        mock_browser_class.return_value = mock_browser

        # Setup requests mock
        mock_response = Mock()
        mock_response.content.decode.return_value = "<html>Test from requests</html>"
        mock_requests_get.return_value = mock_response

        # Create scraper with manual proxy
        scraper = DynamicScrapingNews("https://example.com", manual_proxy="192.168.1.1:8080")

        # Test _get_html
        result = scraper._get_html("https://test.com")

        # Verify results
        assert result == "<html>Test from requests</html>"
        mock_requests_get.assert_called_with(
            "https://test.com",
            headers={'User-Agent': "Mozilla/5.0 Test"},
            proxies={'http': 'http://192.168.1.1:8080', 'https': 'http://192.168.1.1:8080'},
            timeout=30
        )

    @patch('pocong.media_spiders.requests.get')
    @patch('pocong.media_spiders.mechanize.Browser')
    @patch('pocong.media_spiders.UserAgent')
    def test_get_html_without_proxy(self, mock_ua, mock_browser_class, mock_requests_get):
        """Test _get_html without proxy."""
        # Setup mocks
        mock_ua_instance = Mock()
        mock_ua_instance.random = "Mozilla/5.0 Test"
        mock_ua.return_value = mock_ua_instance

        # Make mechanize fail to test requests path
        mock_browser = Mock()
        mock_browser.open.side_effect = Exception("Mechanize failed")
        mock_browser_class.return_value = mock_browser

        # Setup requests mock for first call (with proxy=None)
        mock_response = Mock()
        mock_response.content.decode.return_value = "<html>Test without proxy</html>"
        mock_requests_get.return_value = mock_response

        # Create scraper without proxy
        scraper = DynamicScrapingNews("https://example.com", use_proxy=False)

        # Test _get_html
        result = scraper._get_html("https://test.com")

        # Verify results
        assert result == "<html>Test without proxy</html>"
        mock_requests_get.assert_called_with(
            "https://test.com",
            headers={'User-Agent': "Mozilla/5.0 Test"},
            proxies=None,
            timeout=30
        )

    def test_remove_html_tags(self):
        """Test _remove_html_tags method."""
        scraper = DynamicScrapingNews("https://example.com", use_proxy=False)
        html_text = "<p>Hello <b>world</b>!</p>"
        result = scraper._remove_html_tags(html_text)
        assert result == "Hello world!"

    def test_get_media_from_url(self):
        """Test _get_media method."""
        scraper = DynamicScrapingNews("https://example.com", use_proxy=False)

        # Test with simple domain
        result = scraper._get_media("https://www.cnn.com/news/article")
        assert result == "cnn"

        # Test with subdomain
        result = scraper._get_media("https://sport.detik.com/news")
        assert result == "detik"

        # Test with .co. domain
        result = scraper._get_media("https://www.bbc.co.uk/news")
        assert result == "bbc"
