#!/usr/bin/env python3
import json
import copy
from math import ceil
from time import sleep
from configparser import ConfigParser
import re
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

    def _post(self, url_suffix, payload):
        url = '{prefix}{suffix}'.format(prefix=self.url_prefix, suffix=url_suffix)
        response = self.session.post(url, json=payload)
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

    def list_locations(self):
        response, _ = self._get('locations.json')
        return response['locations']

    def update_product(self, product_id, updated_properties):
        url_suffix = 'products/{product_id}.json'.format(product_id=product_id)
        payload = {
            'product': updated_properties
        }
        self._put(url_suffix, payload)

    def connect_inventory_item(self, inventory_item_id, location_id):
        payload = {
            'inventory_item_id': inventory_item_id,
            'location_id': location_id
        }
        self._post('inventory_levels/connect.json', payload)


def associate_locations(profile, dry_run=True, exit_on_first=False):
    client = Client(profile)

    # Get all locations
    location_ids = [x['id'] for x in client.list_locations() if str(x['id']) != '5868650555']
    print('Found locations [{}]'.format(', '.join(str(x) for x in location_ids)))

    products = client.list_products()
    for product in products:
        product_title = product['title']

        print('Updating product [{}]...'.format(product_title))

        for variant in product.get('variants', []):
            variant_id = variant['id']
            inventory_item_id = variant['inventory_item_id']
            for location_id in location_ids:
                if not dry_run:
                    client.connect_inventory_item(inventory_item_id, location_id)
                print('{}\t{}\t{}'.format(variant_id, inventory_item_id, location_id))

        if exit_on_first:
            exit(0)


def main():
    associate_locations('aitw', dry_run=False, exit_on_first=True)


if __name__ == '__main__':
    main()
