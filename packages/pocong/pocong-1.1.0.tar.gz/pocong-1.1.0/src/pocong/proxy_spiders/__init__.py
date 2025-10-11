# Init file for spiders module to make it a package
import random

import requests


class GetProxy():
    '''
    Class to get proxies using Scrapy spiders and validate them.
    '''
    def __init__(self):
        self._items = []

    def _check_proxy(self, x):
        proxy = f"http://{x['ip']}:{x['port']}"
        try:
            response = requests.get("https://httpbin.org/ip", proxies={'https': proxy}, timeout=10)
            if response.status_code == 200 and response.json().get('origin') == x['ip']:
                return response.status_code
            return 0
        except requests.RequestException:
            return 0

    def _get_proxy_from_scrape(self):
        import subprocess
        import sys
        import json
        # Run the spider in a subprocess to avoid reactor restart error
        code = (
            'import pandas as pd;'
            'from scrapy.crawler import CrawlerProcess;'
            'from pocong.proxy_spiders.spiders.free_proxy_list_net_spider import ProxySpider;'
            'from pocong.proxy_spiders.pipelines import collected_items;'
            'process = CrawlerProcess(settings={"LOG_LEVEL": "ERROR", "ITEM_PIPELINES": {"pocong.proxy_spiders.pipelines.Pipelines": 1}});'  # noqa: E501
            'process.crawl(ProxySpider);'
            'process.start();'
            'process.stop();'
            'df = pd.DataFrame(collected_items);'
            'df = df[df["https"] == "yes"];'
            'df = df.drop_duplicates(subset=["ip", "port"]);'
            'print(df.to_json(orient="records"))'
        )
        result = subprocess.run([sys.executable, '-c', code], capture_output=True, text=True)
        proxies_json = json.loads(result.stdout.strip()) if result.stdout.strip() else []
        return proxies_json

    def get_proxy(self):
        '''
        Get a working proxy from the list of proxies.
        parameter: None
        return: dict or None
        '''
        proxies_json = self._get_proxy_from_scrape()
        for proxy in proxies_json:
            if self._check_proxy(proxy) == 200:
                return proxy

    def get_proxy_random(self):
        '''
        Get a random working proxy from the list of proxies.
        parameter: None
        return: dict or None
        '''
        proxies_json = self._get_proxy_from_scrape()
        retry = 0
        proxy = None
        while retry < 20:
            retry += 1
            proxy = random.choice(proxies_json)
            if self._check_proxy(proxy) == 200:
                break
        return proxy
