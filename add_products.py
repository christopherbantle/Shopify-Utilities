import requests
import json
from time import sleep
from configparser import ConfigParser

config_parser = ConfigParser()
config_parser.read('.credentials')

api_key = config_parser['default']['API_KEY']
password = config_parser['default']['PASSWORD']
store_url_prefix = config_parser['default']['STORE_URL_PREFIX']

url_prefix = 'https://%s:%s@%s.myshopify.com/admin/' % (api_key, password, store_url_prefix)

session = requests.Session()

session.headers.update({'Content-Type': 'application/json'})

payload = {
  "product": {
    "title": "API test 2",
    "body_html": "<strong>Good snowboard!</strong>",
    "vendor": "Test",
    "product_type": "Test",
    "tags": "Emotive, Flash Memory, MP3, Music",
    "variants": [
      {
        "option1": "Blue",
        "option2": "155",
        "price": "200.00"
      },
      {
        "option1": "Black",
        "option2": "159",
        "price": "400.00"
      }
    ],
    "options": [
      {
        "name": "Color"
      },
      {
        "name": "Size"
      }
    ],
    "images": [
          {
              "src": "https://static01.nyt.com/images/2018/07/22/opinion/sunday/22loose/22loose-superJumbo.jpg?quality=90&auto=webp"
          }
    ]
  }
}

products_url = url_prefix + 'products.json'

response = session.post(products_url, json=payload)

if response.status_code != 201:
    raise Exception('Status code: [%d] Unable to post with URL: [%s]' % (response.status_code, products_url))

sleep(0.5)

product = json.loads(response.text)['product']

product_id = product['id']

image_url = url_prefix + 'products/%s/images.json' % product_id

