from bs4 import BeautifulSoup
from collections import namedtuple
from datetime import datetime
import simplejson
import json
import requests
import re
import os.path

# Initial iteration, set the template for each product
# Second iteration, compare to the previous -> objects


class Product(object):
    title = ""
    array_of_resealed_prices = []
    date_scrapped = ""
    number_of_resealed_products = 0

    def __init__(self, title, array_of_resealed_prices, date_scrapped, number_of_resealed_products):
        self.title = title
        self.array_of_resealed_prices = array_of_resealed_prices
        self.date_scrapped = date_scrapped
        self.number_of_resealed_products = number_of_resealed_products


def make_product(title, number_of_resealed_products, array_of_resealed_prices, date_scrapped):
    Product = namedtuple(
        'Product', 'title number_of_resealed_products array_of_resealed_prices date_scrapped')
    product = Product(title, number_of_resealed_products, array_of_resealed_prices,
                      date_scrapped)
    return product


new_list_of_products = []
array_of_formatted_prices = []
now = datetime.now()
all_products_selector = '.panel-resealed-products .product-resealed-price'
number_of_resealed_products = 0

# Get the list of links from file
with open('links.txt', 'r') as f:
    linksList = f.read().splitlines()

# Navigate to each link and create a list of objects from the results
for link in linksList:
    source = requests.get(link)
    content = source.content
    soup = BeautifulSoup(content, "lxml")

    # Title
    title = soup.select('.page-title')[0].text

    # Array of all products
    array_of_resealed_prices = soup.find_all(
        'p', {'class': 'product-resealed-price'})

    for el in array_of_resealed_prices:
        formattedItem = el.text.strip()
        intParsedItem = re.sub(r"\D", "", formattedItem)
        array_of_formatted_prices.append(int(intParsedItem[:-2]))

    number_of_resealed_products = len(array_of_formatted_prices)

    # Date
    date_scrapped = now.strftime("%d/%m/%Y, %H:%M:%S")

    # Create the object
    final_product = make_product(
        title.strip(), number_of_resealed_products, array_of_formatted_prices, date_scrapped)

    new_list_of_products.append(final_product)

    # Empty the array so it can hold only the values of the current Product
    array_of_formatted_prices = []
    number_of_resealed_products = 0


# print(new_list_of_products)


products_json_file = 'products.json'

# Check if the json is already created
if(os.path.exists(products_json_file)):
    old_list_of_products = []
    with open('products.json') as json_file:
        data = json.load(json_file)
        for product in data['Products']:
            objectified_product = make_product(
                product['title'], product['number_of_resealed_products'], product['array_of_resealed_prices'], product['date_scrapped'])
            old_list_of_products.append(objectified_product)

    # Compare the lists
    print('Old list')
    print(old_list_of_products)
    print('New list')
    print(new_list_of_products)

    # To do
    # Compare the old and new list of products
    # If there are differences, return them (link + number of products in resealed)


else:
    # Write the json
    current_content = {
        "Products": [

        ]
    }
    current_content["Products"].append(new_list_of_products)
    # Open the json file
    print('Opening json file...')
    f = open(products_json_file, "w+")
    now_content = simplejson.dumps(current_content)
    f.write(now_content)
