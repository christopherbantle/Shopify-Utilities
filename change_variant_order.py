#!/usr/bin/env python3
import json
from math import ceil
from time import sleep
from configparser import ConfigParser
import re
import yaml
import requests


class Client:

    credentials_file = '.credentials'

    def __init__(self, profile):
        config_parser = ConfigParser()
        config_parser.read(Client.credentials_file)
        credentials = config_parser[profile]
        self.url_prefix = 'https://{key}:{password}@{url_prefix}.myshopify.com/admin/api/2020-04/'.format(
            key=credentials['API_KEY'],
            password=credentials['PASSWORD'],
            url_prefix=credentials['STORE_URL_PREFIX']
        )
        self.session = requests.Session()
        self.session.headers.update({'Content-Type': 'application/json'})

    def _get(self, url_suffix, parameters=None, url=None):
        kwargs = {}
        if url is None:
            url = '{prefix}{suffix}'.format(prefix=self.url_prefix, suffix=url_suffix)
            if parameters is not None:
                kwargs['params'] = parameters
        response = self.session.get(url, **kwargs)
        response.raise_for_status()
        sleep(0.5)
        next_url_suffix = re.search('<(.*)>', response.headers['Link']).group(1) if response.headers.get('Link') else None
        next_url = '{}/{}'.format(self.url_prefix, next_url_suffix.split('2020-04/')[1]) if next_url_suffix is not None else None
        return json.loads(response.text), next_url

    def _put(self, url_suffix, payload):
        url = '{prefix}{suffix}'.format(prefix=self.url_prefix, suffix=url_suffix)
        response = self.session.put(url, json=payload)
        response.raise_for_status()
        sleep(0.5)

    def get_product_count(self):
        return self._get('products/count.json')[0]['count']

    def list_products(self, fields=None):
        if fields is None:
            fields = ['id', 'title', 'variants']
        num_pages = ceil(self.get_product_count() / 250)
        products = []
        url = None
        for i in range(num_pages):
            parameters = {
                'limit': 250,
                'fields': ','.join(fields),
                'product_type': 'Photo'
            }
            response, url = self._get('products.json', parameters=parameters, url=url)
            products.extend(response['products'])
        return products

    def update_product(self, product_id, updated_properties):
        url_suffix = 'products/{product_id}.json'.format(product_id=product_id)
        payload = {
            'product': updated_properties
        }
        self._put(url_suffix, payload)


def change_format_name(profile, dry_run=True):
    client = Client(profile)

    products = client.list_products()
    for product in products:
        product_id = product['id']
        product_title = product['title']

        updated_product = {
            'id': product_id,
            'variants': []
        }
        for variant in product['variants']:
            variant_id = variant['id']
            cropping = variant['option1']
            variant_format = variant['option2']
            size = variant['option3']

            if variant_format == 'Natural Wood Frame':
                change = True
            else:
                change = False

            updated_variant = {
                'id': variant_id
            }
            if change:
                updated_variant['option2'] = 'Canadian Wood Frame'

            updated_product['variants'].append(updated_variant)

            print(
                '{title:<30}{cropping:<15}{format:<25}{size:<15}{change}'.format(
                    title=product_title,
                    cropping=cropping,
                    format=updated_variant.get('option2', variant['option2']),
                    size=size,
                    change=change
                )
            )

        if not dry_run:
            client.update_product(product_id, updated_product)


# def change_prices(profile, dry_run=True):
#     client = Client(profile)
#
#     products = client.list_products()
#     for product in products:
#         product_id = product['id']
#         product_title = product['title']
#
#         updated_product = {
#             'id': product_id,
#             'variants': []
#         }
#         for variant in product['variants']:
#             variant_id = variant['id']
#             cropping = variant['option1']
#             variant_format = variant['option2']
#             size = variant['option3']
#             original_price = variant['price']
#
#             if product_title not in titles_to_exclude and \
#                     cropping in mapping and \
#                     variant_format in mapping[cropping] and \
#                     size in mapping[cropping][variant_format]:
#                 new_price = mapping[cropping][variant_format][size]
#                 change = True
#             else:
#                 new_price = original_price
#                 change = False
#
#             updated_variant = {
#                 'id': variant_id
#             }
#             if change:
#                 updated_variant['price'] = new_price
#
#             updated_product['variants'].append(updated_variant)
#
#             print(
#                 '{title:<30}{cropping:<15}{format:<25}{size:<15}{original_price:<15}{new_price:<15}{change}'.format(
#                     title=product_title,
#                     cropping=cropping,
#                     format=variant_format,
#                     size=size,
#                     original_price=original_price,
#                     new_price=new_price,
#                     change=change
#                 )
#             )
#
#         if not dry_run:
#             client.update_product(product_id, updated_product)


def main():
    change_format_name('aitw', dry_run=False)


if __name__ == '__main__':
    main()
