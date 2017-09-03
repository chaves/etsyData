import logging
import requests
from time import gmtime, strftime
from urllib import parse
import configparser

logger = logging.getLogger(__name__)

config_parser = configparser.ConfigParser()
config_parser.read('etsy.conf')


class EtsyApi(object):

    def __init__(self):
        self.api_key = config_parser.get('API', 'api_key')
        self.api_en_point = config_parser.get('API', 'end_point')
        self.get_seller_taxonomy_method = config_parser.get('API_METHODS', 'getSellerTaxonomy')

    @staticmethod
    def get_date_now():
        return strftime("%Y-%m-%d", gmtime())

    @staticmethod
    def get_date_time_now():
        return strftime("%Y-%m-%d %H:%M:%S", gmtime())

    def request_url(self, method, params=None):
        url = '{endpoint}{method}?api_key={api_key}{params}'.format(
            endpoint=self.api_en_point,
            method=method,
            api_key=self.api_key,
            params='&{}'.format(parse.urlencode(params) if params else ''),
        )
        return url

    def get(self, method, params=None, timeout=5):
        url = self.request_url(method, params)
        response = requests.get(url, timeout=timeout)

        if response.status_code != 200:
            logger.warning('Response si not 200! reason: {}, because: {}'.format(
                response.status_code, response.text
            ))
            return

        data = response.json()
        return data and data['results'][0] if data['count'] == 1 else data['results']

    def get_seller_taxonomy(self):
        return self.get(self.get_seller_taxonomy_method)

    def get_listing(self, listing_id):
        return self.get(
            'listings/{}'.format(listing_id),
            {'includes': 'MainImage,Shop'},
        )

    def get_shop(self, shop_id):
        path = 'shops/{}'.format(shop_id)
        data = self.get(path)

        if not data:
            return

        data['more'] = self.get('{}/about'.format(path))
        return data

    def get_shop_listings(self, shop_id, page=1):
        return self.get(
            'shops/{}/listings/active'.format(shop_id),
            {'includes': 'MainImage', 'limit': 10, 'page': page},
        )

    @classmethod
    def parse_listing(cls, d):
        img = d.get('MainImage', {})
        shop = d.get('Shop', {})

        entry = {
            'title': d.get('title'),
            'state': d.get('state') or 'NA',
            'price': d.get('price'),
            'currency': d.get('currency_code'),
            'tags': d.get('tags'),
            'materials': d.get('materials'),
            'style': d.get('style'),
            'taxonomy_old': d.get('category_path'),
            'taxonomy': d.get('taxonomy_path'),
            'views': d.get('views', 0),
            'favorers': d.get('num_favorers', 0),
            'image': img.get('url_170x135', '').replace('170x135', '340x270'),
            'seller_id': shop.get('shop_id'),
            'last_synced': strftime("%Y-%m-%d %H:%M:%S", gmtime()),
            # gmtime() plutôt que localtime() : plus fiable = 2 heures de moins que Paris
            # Paris = (UTC+2)
        }

        return entry

    @classmethod
    def parse_shop(cls, d):
        story, social = None, None
        if d['more']:
            story = d['more']['story']
            links = d['more'].get('related_links', {})
            social = {
                l['title']: l['url'] for l in (
                    links.values() if type(links) == dict else (links or [])
                )
            }

        entry = {
            'name': d['shop_name'],
            'title': d['title'],
            'icon_url': d['icon_url_fullxfull'],
            'num_favorers': d.get('num_favorers', 0),
            'listings_all_count': d['listing_active_count'],
            'story': story,
            'social': social or None,
        }

        return entry
