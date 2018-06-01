import re

import scrapy
from scrapy.http import Request
import logging


def get_logger(desc, suffix):
    logger = logging.getLogger(desc)
    logger.setLevel(logging.DEBUG)

    fn = logging.FileHandler(desc + '.' + suffix)
    fmt = '%(message)s'
    formatter = logging.Formatter(fmt)
    fn.setFormatter(formatter)

    logger.addHandler(fn)
    return logger


def read_file():
    f = open('site.txt', 'r')
    sites = []
    for line in f:
        sites.append(line.replace('\n', ''))
    print(sites)
    return sites


logger = get_logger('trade', 'csv')
error_logger = get_logger('error_site', 'txt')


class TradeSpider(scrapy.Spider):
    name = "trade"

    # start_urls = [
    #     "https://m.1688.com/offer/529508311398.html?spm=a26g8.7664810.0.0",
    #     'https://m.1688.com/offer/570711189567.html',
    #     'https://m.1688.com/offer/553472663656.html'
    # ]

    def __init__(self):
        super().__init__()
        self.start_urls = read_file()

    def parse(self, response):
        try:
            url = re.search('detailUrl\":\"(.+?)\"', response.text).group(1)
            title = response.xpath("//h1[@class='d-title']/span/text()").extract_first()
            price = re.search('priceRanges\":\[{\"price\":\"(.+?)\"', response.text).group(1)
            product_no = re.search('{\"name\":\"货号\",\"value\":\"(.+?)\"', response.text).group(1)
        except Exception:
            error_logger.log(response.url)
            return

        if url.startswith("//"):
            url = "https:" + url
        print(url)
        request = Request(url, callback=self.parse_detail)
        request.meta['title'] = title
        request.meta['price'] = price
        request.meta['product_no'] = product_no
        request.meta['url'] = response.url
        yield request

    def parse_detail(self, response):

        # name = re.search('【名称】：(.+?)<', response.text).group(1).replace(',', '')
        try:
            shape = re.search('【形状】：(.+?)<', response.text).group(1).replace(',', '')

            size = re.search('【尺寸】：(.+?)<', response.text).group(1).replace(',', '')
            weight = re.search('【克重】：(.+?)<', response.text).group(1).replace(',', '')
            texture = re.search('【材质】：(.+?)<', response.text).group(1).replace(',', '')
        except Exception:
            error_logger.debug(response.meta['url'])
            return
        title = response.meta['title']
        price = response.meta['price']
        product_no = response.meta['product_no']
        print('title------' + title)
        print('price----' + str(price))
        print('product_no------' + product_no)

        print(size)
        print(weight)
        print(texture)

        logger.debug(response.meta['url'], title.replace(',', '') + "," + price + ", " + product_no + "," + shape + "," + size + "," + weight + "," + texture)
