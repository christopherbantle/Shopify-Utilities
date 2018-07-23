# Shopify-Utilities

In order to use these utilities, you must have a `.credentials` file with the following format:

```
[PROFILE NAME]
API_KEY = API KEY
PASSWORD = PASSWORD
STORE_URL_PREFIX = *STORE URL PREFIX (e.g. my-store)*
```

## change_template_based_on_product_type.py
Simply define a mapping from product type to template, and then you can run this script to update your products accordingly.  This is helpful given that, as of July 2018, it is not possible to specify the template for products when uploading them via a csv file.

## delete_products.py
Use this script to delete all of the products in your store (can be modified easily to delete only products with certain attributes).
