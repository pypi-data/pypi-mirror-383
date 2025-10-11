import scrapy


class ProxySpider(scrapy.Spider):
    name = "example"
    start_urls = [
        'https://free-proxy-list.net/en/',
    ]

    def parse(self, response):
        # Extract proxy table rows
        rows = response.css('table tbody tr')
        for row in rows:
            columns = row.css('td')
            if len(columns) >= 8:
                yield {
                    'ip': columns[0].css('::text').get(),
                    'port': columns[1].css('::text').get(),
                    'code': columns[2].css('::text').get(),
                    'country': columns[3].css('::text').get(),
                    'anonymity': columns[4].css('::text').get(),
                    'google': columns[5].css('::text').get(),
                    'https': columns[6].css('::text').get(),
                    'last_checked': columns[7].css('::text').get(),
                }
