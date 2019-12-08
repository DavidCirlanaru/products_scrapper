from bs4 import BeautifulSoup
from collections import namedtuple
from datetime import datetime
from deepdiff import DeepDiff
from pprint import pprint
from db import add_user, list_user
import simplejson
import json
import requests
import re
import os.path
import time

telegram_url = 'https://www.telegram.me'
bot_name = 'emag_scrapper_bot'

# Very secret bot token, might wanna hide it in the future somehow..
bot_token = '974325358:AAHMadWgjB59AARPGo95_ASE_ORoPspATLk'
updates_url = f'https://api.telegram.org/bot{bot_token}/getUpdates'

liviu_chat_id = '358903325'
david_chat_id = '715166577'

product_title = ''
product_original_price = 0
product_smallest_resealed_price = 0
product_url = ''
product_date_scrapped = ''


# To do
# funct (username), when called, look for the user in the database and get his links
# create a json with the results for that user.
# When you add a new element, the array of urls becomes array of objects
# name
# products[
# title
# original_price
# number_of_resealed_products
# array_of_resealed_prices
# product_url
# ]
    

class Product(object):
    title = ""
    original_price = ""
    array_of_resealed_prices = []
    number_of_resealed_products = 0

    def __init__(self, title, original_price, array_of_resealed_prices, number_of_resealed_products, product_url):
        self.title = title
        self.original_price = original_price
        self.array_of_resealed_prices = array_of_resealed_prices
        self.number_of_resealed_products = number_of_resealed_products
        self.product_url = product_url


def make_product(title, original_price, number_of_resealed_products, array_of_resealed_prices, product_url):
    Product = namedtuple(
        'Product', 'title original_price number_of_resealed_products array_of_resealed_prices product_url')
    product = Product(title, original_price, number_of_resealed_products,
                      array_of_resealed_prices, product_url)

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


def remove_url_parameters(url):
    url.strip()
    if(url.find('?') != -1):
        return url.split('?', 1)[0]
    return url


# Get the list of links from txt file
with open('links.txt', 'r') as f:
    linksList = f.read().splitlines()

# Navigate to each link and create a list of objects from the results
for link in linksList:
    # time.sleep(3)
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
        title.strip().replace('"', ' Inch'), final_parsed_price, number_of_resealed_products, array_of_formatted_prices, remove_url_parameters(link))

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
            product['title'], product['original_price'], product['number_of_resealed_products'], product['array_of_resealed_prices'], product['product_url'])

        old_list_of_formatted_products.append(old_object)

    # DeepDiff() checks for any differences and returns a DeepDiff object
    analyzed_object = DeepDiff(
        new_list_of_products, old_list_of_formatted_products)

    analyzed_object.to_dict()

    for key, value in analyzed_object['type_changes'].items():
        # Send what's new in the new values list

        if (value['new_value'] != value['old_value']):
            print('Found changes, sending the notification...')
            product_title = value['new_value'].title
            product_original_price = f"{value['new_value'].original_price} RON"
            if (value['new_value'].array_of_resealed_prices != []):
                product_smallest_resealed_price = f"{min(value['new_value'].array_of_resealed_prices)} RON"
            else:
                product_smallest_resealed_price = 'Nu exista resigilate.'
            product_url = value['new_value'].product_url
            # product_date_scrapped = date_scrapped

            notification_text = "A aparut o modificare la produsul: " + product_title + " |" + " pret: " + \
                product_original_price + " |" + " cel mai ieftin resigilat: " + \
                product_smallest_resealed_price + " | " + product_url

            print(product_url)
            send_message_url = "https://api.telegram.org/bot"+bot_token+"/sendMessage?chat_id=" + \
                david_chat_id+"&text="+notification_text+"&parse_mode=markdown"
            requests.post(send_message_url)

            found_changes = True
            print('Notifications sent succesfully.')

    # Overwrite the existing json file with the new list
    if (found_changes):
        print('Overwriting the existing json file...')
        f = open(products_json_file, "w+")
        now_content = simplejson.dumps(new_list_of_products)
        f.write(now_content)
        found_changes = False
    else:
        print('Found nothing. Script closing..')

# Else create the json file
else:
    print('Creating the first json file...')
    f = open(products_json_file, "w+")
    now_content = simplejson.dumps(new_list_of_products)
    f.write(now_content)
    print('First scrape completed successfully.')
