from bs4 import BeautifulSoup
from datetime import datetime
import db
import requests
import re
import time

# To do
# Hide the telegram token
# TEst what happens when products array exists and user adds or removes urls..
# Test multiple changes appear..

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


# =================== Scrapping the data


users = db.get_all_users()
for user in users:
    current_username = user['username']
    linksList = user['urls']
    differences = []
    old_list_of_products = []
    new_list_of_products = []
    current_chat_id = db.get_chat_id(current_username)

    for link in linksList:
        array_of_reselead_prices = []
        print(f'Scrapping {link}...')
        time.sleep(2)

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
        # date_scrapped = now.strftime("%d/%m/%Y, %H:%M:%S")

        # Create the Product object using the scrapped data and add it to $new_list_of_products
        new_product = {
            'title': title.strip().replace('"', ' Inch'),
            'original_price': final_parsed_price,
            'number_of_resealed_products': number_of_resealed_products,
            'array_of_resealed_prices': array_of_formatted_prices,
            'product_url': remove_url_parameters(link)
        }

        new_list_of_products.append(new_product)

        size_of_products_array = len(new_list_of_products)
        print(f'Products array size: {size_of_products_array}')
        print(f'Links list size: {len(linksList)}')

        # Reinit vars
        array_of_formatted_prices = []
    # If the size of the urls array == the size of the new products array
    if (size_of_products_array is not None and size_of_products_array == len(linksList)):
        print('Scrapped all products from url array..')
        this_user = db.list_user(current_username)

        try:
            old_list_of_products = this_user['products']
        except KeyError:
            old_list_of_products = []
            print('Products array not available yet..')

        for new_product in new_list_of_products:
            db.add_product_data(current_username, new_product)
            print(f"Added ${new_product['title']} for ${current_username}..")

        if (not old_list_of_products):
            print('Old list is empty')
        else:
            print(f'new: {new_list_of_products}, {type(new_list_of_products)}')
            print(f'old: {old_list_of_products, type(old_list_of_products)}')

            differences = [i for i in new_list_of_products if i not in old_list_of_products] \
                + [j for j in old_list_of_products if j not in new_list_of_products]

            # If there are no changes..
            if (not differences):
                print('No changes.')

            # If there are changes found..
            else:
                db.overwrite_product_data(
                    current_username, new_list_of_products)
                print(f'Found this changes: {differences}')
                for product in differences[::2]:
                    print(product['title'])
                new_product = None

                print('Found changes, sending the notification...')
                # ===================

                product_title = product['title']
                product_original_price = f"{product['original_price']} RON"
                if (product['array_of_resealed_prices'] != []):
                    product_smallest_resealed_price = f"{min(product['array_of_resealed_prices'])} RON"
                else:
                    product_smallest_resealed_price = 'Nu exista resigilate.'
                product_url = product['product_url']
                # product_date_scrapped = date_scrapped

                notification_text = "Salut " + current_username + ", aparut o modificare la produsul: " + product_title + " |" + " pret: " + \
                    product_original_price + " |" + " cel mai ieftin resigilat: " + \
                    product_smallest_resealed_price + " | " + product_url
                print(notification_text)

                send_message_url = "https://api.telegram.org/bot"+bot_token+"/sendMessage?chat_id=" + \
                    str(current_chat_id)+"&text=" + \
                    notification_text+"&parse_mode=markdown"
                requests.post(send_message_url)
                # To do, function to accept the message as parameter from the emag_bot.py

        message_data = None
        differences = []
        old_list_of_products = []
        new_list_of_products = []
        array_of_resealed_prices = []
        this_user = None
        array_of_formatted_prices = []
        number_of_resealed_products = 0
        current_chat_id = None
        print('Process ended..')
