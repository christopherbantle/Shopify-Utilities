import requests
import json
from math import ceil
from time import sleep
from configparser import ConfigParser

PRODUCT_TYPE_TO_TEMPLATE = {
    "Photo": "regular-photo"
}

config_parser = ConfigParser()
config_parser.read('.credentials')

api_key = config_parser['aitw']['API_KEY']
password = config_parser['aitw']['PASSWORD']
store_url_prefix = config_parser['aitw']['STORE_URL_PREFIX']

url_prefix = 'https://%s:%s@%s.myshopify.com/admin/' % \
             (api_key, password, store_url_prefix)

count_url = url_prefix + 'products/count.json'

session = requests.Session()

session.headers.update({'Content-Type': 'application/json'})

parameters = {
    'product_type': 'Photo'
}

response = session.get(count_url, params=parameters)

if response.status_code != 200:
    raise Exception('Status code: [%d] Unable to get URL: [%s]' %
                    (response.status_code, count_url))

sleep(0.5)

number_of_products = json.loads(response.text)['count']

num_pages = ceil(number_of_products / 250)

for i in range(num_pages):
    products_url = url_prefix + 'products.json'

    parameters = {
        'page': i + 1,
        'limit': 250,
        'fields': 'id,variants',
        'product_type': 'Photo'
    }

    response = session.get(products_url, params=parameters)

    if response.status_code != 200:
        raise Exception('Status code: [%d] Unable to get with URL: [%s]' %
                        (response.status_code, products_url))

    sleep(0.5)

    products = json.loads(response.text)['products']

    for product in products:
        product_id = product['id']
        variants = product['variants']

        for variant in variants:
            variant_id = variant['id']
            option2 = variant.get('option2')

            if option2 == 'Printed Photo Only':
                payload = {
                    'variant': {
                        'id': variant_id,
                        'weight': 0
                    }
                }

                variant_url = url_prefix + 'variants/%d.json' % variant_id

                response = session.put(variant_url, json=payload)

                if response.status_code != 200:
                    raise Exception(
                        'Status code: [%d] Unable to put with URL: [%s]' %
                        (response.status_code, variant_url))

                print('Put with url [%s]' % variant_url)

                sleep(0.5)
