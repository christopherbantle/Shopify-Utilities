#!/usr/bin/env python3
import json
from math import ceil
from time import sleep
from configparser import ConfigParser
import yaml
import requests


class Client:

    credentials_file = '.credentials'

    def __init__(self, profile):
        config_parser = ConfigParser()
        config_parser.read(Client.credentials_file)
        credentials = config_parser[profile]
        self.url_prefix = 'https://{key}:{password}@{url_prefix}.myshopify.com/admin/'.format(
            key=credentials['API_KEY'],
            password=credentials['PASSWORD'],
            url_prefix=credentials['STORE_URL_PREFIX']
        )
        self.session = requests.Session()
        self.session.headers.update({'Content-Type': 'application/json'})

    def _get(self, url_suffix, parameters=None):
        url = '{prefix}{suffix}'.format(prefix=self.url_prefix, suffix=url_suffix)
        kwargs = {}
        if parameters is not None:
            kwargs['params'] = parameters
        response = self.session.get(url, **kwargs)
        response.raise_for_status()
        sleep(0.5)
        return json.loads(response.text)

    def _put(self, url_suffix, payload):
        url = '{prefix}{suffix}'.format(prefix=self.url_prefix, suffix=url_suffix)
        response = self.session.put(url, json=payload)
        response.raise_for_status()
        sleep(0.5)

    def get_product_count(self):
        return self._get('products/count.json')['count']

    def list_products(self, fields=None):
        if fields is None:
            fields = ['id', 'title', 'variants']
        num_pages = ceil(self.get_product_count() / 250)
        products = []
        for i in range(num_pages):
            parameters = {
                'page': i + 1,
                'limit': 250,
                # 'fields': ','.join(fields),
                'product_type': 'Photo'
            }
            response = self._get('products.json', parameters=parameters)
            products.extend(response['products'])
        return products

    def update_product(self, product_id, updated_properties):
        url_suffix = 'products/{product_id}.json'.format(product_id=product_id)
        payload = {
            'product': updated_properties
        }
        self._put(url_suffix, payload)


def reverse_discount(mapping_file, profile, dry_run=True):
    client = Client(profile)

    with open(mapping_file) as file:
        mapping = yaml.load(file)

    products = client.list_products()
    for product in products:
        product_id = product['id']
        product_title = product['title']
        tags = product['tags'].split(', ')

        if 'Classics' in tags:
            updated_product = {
                'id': product_id,
                'variants': []
            }
            for variant in product['variants']:
                variant_id = variant['id']
                cropping = variant['option1']
                variant_format = variant['option2']
                size = variant['option3']

                if variant_format in {'Natural Wood Frame', 'Printed Photo Only', 'Matted'}:
                    price = mapping[cropping][variant_format][size]
                    updated_variant = {
                        'id': variant_id,
                        # TODO: Uncomment
                        # 'price': '{:.2f}'.format(price),
                        'compare_at_price': None
                    }

                    updated_product['variants'].append(updated_variant)

                    print(
                        '{title:<30}{cropping:<15}{format:<25}{size:<15}{price:<15}'.format(
                            title=product_title,
                            cropping=cropping,
                            format=variant_format,
                            size=size,
                            price=price
                        )
                    )
                else:
                    updated_product['variants'].append({'id': variant_id})

            if not dry_run:
                print('Updated product [{product_id}]'.format(product_id=product_id))
                client.update_product(product_id, updated_product)


def main():
    reverse_discount('prices.yml', 'aitw', dry_run=False)


if __name__ == '__main__':
    main()
