from bs4 import BeautifulSoup
from collections import namedtuple
from datetime import datetime
import simplejson
import json
import requests
import re
import os.path
from deepdiff import DeepDiff
from pprint import pprint

# To do
# Handle the case where there are new links added to .txt file and the first json is already live.


class Product(object):
    title = ""
    original_price = ""
    array_of_resealed_prices = []
    number_of_resealed_products = 0

    def __init__(self, title, original_price, array_of_resealed_prices, number_of_resealed_products):
        self.title = title
        self.original_price = original_price
        self.array_of_resealed_prices = array_of_resealed_prices
        self.number_of_resealed_products = number_of_resealed_products


def make_product(title, original_price, number_of_resealed_products, array_of_resealed_prices):
    Product = namedtuple(
        'Product', 'title original_price number_of_resealed_products array_of_resealed_prices')
    product = Product(title, original_price, number_of_resealed_products,
                      array_of_resealed_prices)

    return product


# Variables
new_list_of_products = []
array_of_formatted_prices = []
old_list_of_formatted_products = []
number_of_resealed_products = 0
products_json_file = 'products.json'
found_changes = False
now = datetime.now()

# Functions


def parse_to_int(string):
    string.strip()
    return re.sub(r"\D", "", string)


# Get the list of links from txt file
with open('links.txt', 'r') as f:
    linksList = f.read().splitlines()

# Navigate to each link and create a list of objects from the results
for link in linksList:
    source = requests.get(link)
    content = source.content
    soup = BeautifulSoup(content, "lxml")

    # Get the title
    title = soup.select('.page-title')[0].text

    # Get the original price
    original_price = soup.select(
        '.main-product-form .product-new-price')[0].text

    parsed_price = parse_to_int(original_price)
    final_parsed_price = int(parsed_price[:-2])

    # Get the array of all products
    array_of_resealed_prices = soup.find_all(
        'p', {'class': 'product-resealed-price'})

    # Format the array of prices and get the length of the array
    for el in array_of_resealed_prices:
        formattedItem = el.text.strip()
        intParsedItem = parse_to_int(formattedItem)
        array_of_formatted_prices.append(int(intParsedItem[:-2]))

    array_of_formatted_prices.sort()
    number_of_resealed_products = len(array_of_formatted_prices)

    # Get the current date
    date_scrapped = now.strftime("%d/%m/%Y, %H:%M:%S")

    # Create the Product object using the scrapped data and add it to $new_list_of_products
    final_product = make_product(
        title.strip(), final_parsed_price, number_of_resealed_products, array_of_formatted_prices)

    new_list_of_products.append(final_product)

    # Reainitialize the variables for the next iteration
    array_of_formatted_prices = []
    number_of_resealed_products = 0


# Compare with the existing json
if(os.path.exists(products_json_file)):
    with open('products.json') as json_file:
        # Read the current json file

        old_list_of_products = json.load(json_file)

    # Convert the old json to the same obj type as the new list
    for product in old_list_of_products:
        old_object = make_product(
            product['title'], product['original_price'], product['number_of_resealed_products'], product['array_of_resealed_prices'])

        old_list_of_formatted_products.append(old_object)

    # DeepDiff() checks for any differences and returns a DeepDiff object
    analyzed_object = DeepDiff(
        new_list_of_products, old_list_of_formatted_products)

    analyzed_object.to_dict()

    for key, value in analyzed_object['type_changes'].items():
        if (value['new_value'] != value['old_value']):
            print('Found the following changes:')
            pprint(value['new_value'])
            print('Moment scrapped: ' + date_scrapped)
            found_changes = True

    # Overwrite the existing json file with the new list
    if (found_changes):
        print('Overwriting the existing json file...')
        f = open(products_json_file, "w+")
        now_content = simplejson.dumps(new_list_of_products)
        f.write(now_content)

# Else create the json file
else:
    print('Creating the first json file...')
    f = open(products_json_file, "w+")
    now_content = simplejson.dumps(new_list_of_products)
    f.write(now_content)
    print('First scrape completed successfully.')
