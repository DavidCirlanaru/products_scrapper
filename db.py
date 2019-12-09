import pymongo
import collections
from pymongo import MongoClient

# Database init
client = MongoClient()
product_link_list = []
client = MongoClient('mongodb://localhost:27017')
db = client.emag_scrapper
users = db.users
all_users_array = []


def get_all_users():
    for document in users.find():
        all_users_array.append(document)
    return all_users_array


def add_user(username, urls):
    query = users.find_one({"username": username})
    if (query is not None):
        users.find_one_and_update({"username": username},
                                  {"$set": {"urls": urls}}, upsert=True)
        return

    user_data = {
        'username': username,
        'urls': urls
    }
    users.insert_one(user_data)


def list_user(username):
    query = users.find_one({"username": username})
    if (query is not None):
        return query
    print('Could not find the user with that username.')


def delete_link(username, index):
    query = users.find_one({"username": username})
    if (query is not None):
        users.update_one(
            {'username': username}, {'$unset': {f'urls.{index}': 1}})
        users.update_one({'username': username}, {'$pull': {'urls': None}})


def add_product_data(username, product_data):
    users.find_one_and_update({"username": username},
                              {"$set": {
                                  "products": [
                                      {
                                          'title': product_data.title,
                                          'original_price': product_data.original_price,
                                          'number_of_resealed_products': product_data.number_of_resealed_products,
                                          'array_of_resealed_prices': product_data.array_of_resealed_prices,
                                          'product_url': product_data.product_url
                                      }
                                  ]}}, upsert=True)


def products_field_exist(username):
    query = users.find({
        '$and': [
            {'username': username},
            {'products': {'$exists': True}}
        ]
    })

    for result in query:
        if (result is not None):
            return True

    return False

# Get the size of the products array, if it exists