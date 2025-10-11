import datetime as dt
import re

import mechanize
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from html2text import html2text

try:
    from pocong.proxy_spiders import GetProxy
    PROXY_AVAILABLE = True
except ImportError:
    PROXY_AVAILABLE = False


class DynamicScrapingNews():
    def __init__(self, url, use_proxy=True, manual_proxy=None):
        self.url = url
        self.use_proxy = use_proxy
        self.proxy = None

        # Use manual proxy if provided
        if manual_proxy:
            self.proxy = self._format_proxy(manual_proxy)
        # Otherwise, initialize proxy if available and requested
        elif self.use_proxy and PROXY_AVAILABLE:
            try:
                proxy_getter = GetProxy()
                proxy_data = proxy_getter.get_proxy_random()
                if proxy_data:
                    self.proxy = f"http://{proxy_data['ip']}:{proxy_data['port']}"
            except Exception:
                # If proxy initialization fails, continue without proxy
                self.proxy = None

    def _format_proxy(self, proxy):
        """
        Format proxy to ensure it has the correct format.
        Accepts formats like:
        - "ip:port"
        - "http://ip:port"
        - "https://ip:port"
        - {"ip": "x.x.x.x", "port": "xxxx"}
        """
        if isinstance(proxy, dict):
            # If proxy is a dict with ip and port
            if 'ip' in proxy and 'port' in proxy:
                return f"http://{proxy['ip']}:{proxy['port']}"
            else:
                raise ValueError("Manual proxy dict must contain 'ip' and 'port' keys")
        elif isinstance(proxy, str):
            # If proxy is a string
            if proxy.startswith(('http://', 'https://')):
                return proxy
            else:
                # Assume it's in ip:port format
                return f"http://{proxy}"
        else:
            raise ValueError("Manual proxy must be a string or dict")

    def _remove_html_tags(self, text):
        # This regular expression will match any HTML tag and capture its contents.
        html_tags_pattern = r'<.*?>'
        # Use re.sub to replace all matches with an empty string.
        clean_text = re.sub(html_tags_pattern, '', text)
        return clean_text

    def _get_metadata(self, html, list_metadata=['title', 'url', 'image']):
        result = dict()
        for metadata in list_metadata:
            # Define the regular expression pattern
            pattern = r'property="og:{}" content="([^"]+)"'.format(metadata)

            # Search for the pattern in the HTML content
            match = re.search(pattern, html)

            if match:
                # Extract the content from the matched group
                og_content = match.group(1)
                result[metadata] = og_content if '?' not in og_content else og_content.split('?')[0]
            else:
                if metadata == 'url':
                    result[metadata] = self.url if '?' not in self.url else self.url.split('?')[0]
                else:
                    result[metadata] = "Pattern not found in the HTML content."
            result[metadata] = self._remove_html_tags(BeautifulSoup(result[metadata], 'html.parser').get_text())
            result[metadata] = re.sub(r"&amp;", "&", result[metadata])
        return result

    def _clean_html_to_text(self, html):
        # First we remove inline JavaScript/CSS:
        cleaned = re.sub(r"(?is)<(script|style).*?>.*?(</\1>)", "", html.strip())
        # Then we remove html comments. This has to be done before removing regular
        # tags since comments can contain '>' characters.
        cleaned = re.sub(r"(?s)<!--(.*?)-->[\n]?", "", cleaned)
        # Next we can remove the remaining tags:
        cleaned = re.sub(r"(?s)<.*?>", " ", cleaned)
        # Finally, we deal with whitespace
        cleaned = re.sub(r"&nbsp;", " ", cleaned)
        cleaned = re.sub(r"  ", " ", cleaned)
        cleaned = re.sub(r"  ", " ", cleaned)
        text = html2text(cleaned).format('utf-8')
        spe_char = [
            '\\u0621', '\\u0622', '\\u0625', '\\u0627', '\\u0629', '\\u062a', '\\u062b', '\\u062c', '\\u062f',
            '\\u0631', '\\u0632', '\\u0633', '\\u0634', '\\u0636', '\\u0637', '\\u0639', '\\u063a', '\\u0641',
            '\\u0643', '\\u0644', '\\u0645', '\\u0646', '\\u0647', '\\u0648', '\\u064a'
        ]
        for char in spe_char:
            text = text.replace(char, '')
        return text.strip()

    def _get_media(self, url):
        # Define a regular expression pattern to match the main domain (excluding "sport" and subdomains)
        pattern = r"https?://(?:www\.)?(?:[^./]+\.)*([^.]+\.\w+)"

        # Use re.search to find the first match
        match = re.search(pattern, url.replace('.co.', '.'))

        # Extract the matched domain
        if match:
            domain = match.group(1)
            return domain.split('.')[0]
        else:
            return None

    def _get_pubdate(self, html):
        # Define a regular expression pattern to match the content attribute value
        pattern = r'content="(\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2})"'

        # Use re.search to find the first match
        match = re.search(pattern, html)

        # Extract the matched content attribute value
        if match:
            content_value = match.group(1)

            # Convert the content value to a datetime format
            datetime_format = "%Y/%m/%d %H:%M:%S"
            parsed_datetime = dt.datetime.strptime(content_value, datetime_format)

            return parsed_datetime
        else:
            # Define a regular expression pattern to match the content attribute value
            pattern = r'content="(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})"'

            # Use re.search to find the first match
            match = re.search(pattern, html)

            # Extract the matched content attribute value
            if match:
                content_value = match.group(1)

                # Convert the content value to a datetime format
                datetime_format = "%Y-%m-%d %H:%M:%S"
                parsed_datetime = dt.datetime.strptime(content_value, datetime_format)

                return parsed_datetime
            else:
                # Define a regular expression pattern to match the content attribute value
                pattern = r'content="(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\+\d{2}:\d{2})"'

                # Use re.search to find the first match
                match = re.search(pattern, html)

                # Extract the matched content attribute value
                if match:
                    content_value = match.group(1)

                    # Convert the content value to a datetime format
                    datetime_format = "%Y-%m-%dT%H:%M:%S%z"
                    parsed_datetime = dt.datetime.strptime(content_value, datetime_format)

                    return parsed_datetime
                else:
                    return None

    def _get_html(self, url):
        # random useragent
        ua = UserAgent()
        user_agent = ua.random
        headers = {'User-Agent': user_agent}

        # Try with mechanize first (with proxy if available)
        try:
            br = mechanize.Browser()
            br.set_handle_robots(False)
            br.addheaders = [('User-Agent', user_agent)]

            # Set proxy for mechanize if available
            if self.proxy:
                br.set_proxies({'http': self.proxy, 'https': self.proxy})

            html = br.open(url).read().decode('utf-8')
            return html
        except Exception:
            # Fallback to requests (with proxy if available)
            try:
                proxies = {'http': self.proxy, 'https': self.proxy} if self.proxy else None
                response = requests.get(url, headers=headers, proxies=proxies, timeout=30)
                html = response.content.decode('utf-8')
                return html
            except Exception:
                # Final fallback without proxy
                response = requests.get(url, headers=headers, timeout=30)
                html = response.content.decode('utf-8')
                return html

    def scrape(self):
        # get html from url
        html = self._get_html(self.url)

        # get metadata
        metadata = self._get_metadata(html)

        # convert html to text
        text = self._clean_html_to_text(html)

        # get media from url
        media = self._get_media(self.url)

        # get published_date from html
        published_date = self._get_pubdate(html)

        # combine result
        metadata['html'] = html
        metadata['text'] = text
        metadata['media'] = media
        metadata['published_date'] = published_date

        return metadata
