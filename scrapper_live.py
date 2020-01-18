from bs4 import BeautifulSoup
from datetime import datetime
from fake_useragent import UserAgent
import db
import requests
import re
import time
import config

# To do

# Variables
bot_token = config.bot_token
product_title = ''
product_original_price = 0
product_smallest_resealed_price = 0
product_url = ''
new_list_of_products = []
array_of_formatted_prices = []
number_of_resealed_products = 0
now = datetime.now()

ua = UserAgent()


# Function


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
    current_user_id = user['telegram_id']
    current_user_first_name = user['first_name']
    linksList = user['urls']
    differences = []
    old_list_of_products = []
    new_list_of_products = []
    current_chat_id = current_user_id

    for link in linksList:
        array_of_reselead_prices = []
        print(f'Scrapping {link}...')
        headers = {
            'User-Agent': ua.random,
        }

        session = requests.session()
        source = session.get(link, headers=headers)
        content = source.content
        soup = BeautifulSoup(content, "lxml")

        # Get the title
        try:
            if (soup.select('.page-title')[0].text is not None):
                title = soup.select('.page-title')[0].text

            else:
                print("Page/product doesn't exist anymore..")
                continue

        except IndexError:
            print('Blocked by re-captcha..')
            exit()

        try:
            # Get the original price
            if (soup.select(
                    '.main-product-form .product-new-price')[0].text is not None):
                original_price = soup.select(
                    '.main-product-form .product-new-price')[0].text

            parsed_price = parse_to_int(original_price)
            final_parsed_price = int(parsed_price[:-2])

            # Get the array of all products
            if (soup.find_all(
                    'p', {'class': 'product-resealed-price'}) is not None):
                array_of_resealed_prices = soup.find_all(
                    'p', {'class': 'product-resealed-price'})
        except:
            final_parsed_price = '-'
            print('Product not found')
            pass

        # Format the array of prices and get the length of the array
        for el in array_of_resealed_prices:
            formattedItem = el.text.strip()
            intParsedItem = parse_to_int(formattedItem)
            array_of_formatted_prices.append(int(intParsedItem[:-2]))

        array_of_formatted_prices.sort()
        number_of_resealed_products = len(array_of_formatted_prices)

        # Get the current date
        date_scrapped = now.strftime("%d/%m/%Y, %H:%M:%S")
        print(date_scrapped)
        # Create a dict. out of the scraped data
        new_product = {
            'title': title.strip().replace('"', ' Inch'),
            'original_price': final_parsed_price,
            'number_of_resealed_products': number_of_resealed_products,
            'array_of_resealed_prices': array_of_formatted_prices,
            'product_url': remove_url_parameters(link)
        }

        new_list_of_products.append(new_product)

        size_of_products_array = len(new_list_of_products)
        date_scrapped = None
        final_parsed_price = None
        array_of_formatted_prices = []
        ua.update()
        time.sleep(4)

    # If the size of the urls array == the size of the new products array
    if (size_of_products_array is not None and size_of_products_array == len(linksList)):
        print('Scrapped all products from url array..')
        this_user = db.list_user(current_user_id)

        try:
            old_list_of_products = this_user['products']
        except KeyError:
            old_list_of_products = []
            print('Products array not available yet..')

        # Adding the new list of products to the database
        db.add_product_data(current_user_id, new_list_of_products)
        print(f"Added ${new_product['title']} for ${current_user_id}..")

        if (not old_list_of_products):
            print('Old list is empty')
        else:
            differences = [
                i for i in new_list_of_products if i not in old_list_of_products]
            old_values = [
                j for j in old_list_of_products if j not in new_list_of_products]

            if (not differences):
                print('No changes.')

            # If there are changes found..
             # =================== Notifications =================== #
            else:
                db.overwrite_product_data(
                    current_user_id, new_list_of_products)

                for product in differences:
                    print(product['title'])
                    print(product['original_price'])

                    product_title = product['title']
                    product_original_price = f"{product['original_price']} RON"
                    if (product['array_of_resealed_prices'] != []):
                        product_smallest_resealed_price = f"{min(product['array_of_resealed_prices'])} RON"
                    else:
                        product_smallest_resealed_price = ' - '

                    product_url = product['product_url']

                    for old_product in old_values:
                        if (old_product['title'] == product['title']):
                            print(old_product['title'])
                            print(old_product['original_price'])
                            # Old
                            old_product_original_price = f"{old_product['original_price']} RON"

                            if (old_product['array_of_resealed_prices'] != []):
                                old_product_smallest_resealed_price = f"{min(old_product['array_of_resealed_prices'])} RON"
                            else:
                                old_product_smallest_resealed_price = ' - '
                            break

                    print('Found changes, sending the notification...')
                    notification_text = "Salut " + current_user_first_name + ", a aparut o modificare la produsul: " + product_title + " |" + " pret: " + \
                        product_original_price + " |" + " cel mai ieftin resigilat: " + \
                        product_smallest_resealed_price + " | " + product_url + " | " + "pretul anterior: " + \
                        old_product_original_price + " | " + "cel mai ieftin resigilat anterior: " + \
                        old_product_smallest_resealed_price

                    send_message_url = "https://api.telegram.org/bot"+bot_token+"/sendMessage?chat_id=" + \
                        str(current_chat_id)+"&text=" + \
                        notification_text+"&parse_mode=markdown"
                    print(send_message_url)
                    requests.post(send_message_url)

                    new_product = None

        message_data = None
        differences = []
        old_list_of_products = []
        new_list_of_products = []
        array_of_resealed_prices = []
        this_user = None
        array_of_formatted_prices = []
        number_of_resealed_products = 0
        current_chat_id = None
        print('Scrapper finished.')
