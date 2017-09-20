import configparser
import logging
from lxml import html
import lxml
import time
import requests
import os

logger = logging.getLogger(__name__)

config_parser = configparser.ConfigParser()
config_parser.read(os.path.dirname(os.path.abspath(__file__)) + 'etsy.conf')


class EtsyScraping(object):
    
    def __init__(self):
        self.p_home = config_parser.get('PATHS', 'home')
        self.p_cat = config_parser.get('PATHS', 'categories')
        self.params = {'locationQuery': config_parser.get('COUNTRY_CODES', 'current')}
        self.pages_total = 0
        
    def make_category_link(self, path):
        return self.p_cat + path.replace('.', '/')
    
    def get_request(self, url):
        response = requests.get(url, params=self.params)
        if response.status_code != 200:
            logger.warning('Response is not 200! reason: {}, because: {}'.format(
                response.status_code, response.text
            ))
        return response

    def check_status(self, url):
        response = requests.get(url, params=self.params)
        print('{} : {}'.format(response.status_code, url))
        return response.status_code

    @staticmethod
    def get_xml_string_from_response(response):
        content_source = response.text.encode("utf-8")
        return html.document_fromstring(content_source)

    @staticmethod
    def get_max_sub_pages(xml_doc):
        # get page numbers in data-page attribute
        elements = xml_doc.xpath(
            '//nav[contains(@class,"pagination")]/a/@data-page'
        )
        max_pages = 1
        if len(elements) > 0:
            # convert page numbers to integers
            elements_int = [int(i) for i in elements]
            max_pages = max(elements_int)
        return max_pages

    @staticmethod
    def get_shops_xpath(xml_doc):
        shops = xml_doc.xpath(
            ('//div[@class = "col-group overflow-auto pl-xs-0"]//p[@class'
             ' = "text-gray-lighter text-body-smaller display-inline-block mr-xs-1"]/text()')
        )
        return [str(shop) for shop in shops]

    @staticmethod
    def get_products_id_xpath(xml_doc):
        products = xml_doc.xpath(
            '//div[@class = "col-group overflow-auto pl-xs-0"]//div/a/@data-listing-id'
        )
        return [str(product) for product in products]
    
    def get_data_from_sub_pages(self, url, max_pages):
        products = []
        shops = []
        for page in range(2, max_pages):
            time.sleep(3)
            self.params['page'] = page
            response = self.get_request(url)
            print('GET page {} : {}'.format(page, url))
            if response:
                xml_doc = self.get_xml_string_from_response(response)
                products.extend(self.get_products_id_xpath(xml_doc))
                shops.extend(self.get_shops_xpath(xml_doc))
                print('GOT page {} : {}'.format(page, url))
        return products, shops
    
    def get_pages_total(self):
        return self.pages_total

    def get_shops_and_product_ids_from_category(self, path):
    
        url = self.make_category_link(path)
        
        response = self.get_request(url)
        xml_doc = self.get_xml_string_from_response(response)
        print('GOT page 1 : {}'.format(url))
        
        max_pages = self.get_max_sub_pages(xml_doc)
        self.pages_total = max_pages
        print('Max Pages = {}'.format(max_pages))
        
        products = self.get_products_id_xpath(xml_doc)
        shops = self.get_shops_xpath(xml_doc)
        
        print('Products set 1 = {}'.format(products))
        print('Shops set 1 = {}'.format(shops))
        
        more_products, more_shops = self.get_data_from_sub_pages(url, max_pages)
        
        print('Products set 2 = {}'.format(more_products))
        print('Shops set 2 = {}'.format(more_shops))
        
        products.extend(more_products)
        shops.extend(more_shops)
        
        return list(zip(products, shops))
