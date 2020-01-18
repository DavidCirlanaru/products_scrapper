import pymongo
from pymongo import MongoClient

# Database init
client = MongoClient()
product_link_list = []
client = MongoClient('mongodb://127.0.0.1:27017')
db = client.emag_scrapper
users = db.users
all_users_array = []


def get_all_users():
    for document in users.find():
        all_users_array.append(document)
    return all_users_array


def add_user(telegram_id, username, first_name, urls):
    query = users.find_one({"telegram_id": telegram_id})
    if (query is not None):
        users.find_one_and_update({"telegram_id": telegram_id},
                                  {"$set": {"urls": urls}}, upsert=True)
        return

    user_data = {
        'telegram_id': telegram_id,
        'username': username,
        'first_name': first_name,
        'urls': urls
    }
    users.insert_one(user_data)


def list_user(telegram_id):
    query = users.find_one({"telegram_id": telegram_id})
    if (query is not None):
        return query
    print('Could not find the user with that id.')


def delete_link(telegram_id, index):
    query = users.find_one({"telegram_id": telegram_id})
    if (query is not None):
        users.update_one(
            {'telegram_id': telegram_id}, {'$unset': {f'urls.{index}': 1}})
        users.update_one({'telegram_id': telegram_id},
                         {'$pull': {'urls': None}})


def overwrite_product_data(telegram_id, product_data):
    users.find_one_and_update({"telegram_id": telegram_id},
                              {"$set": {
                                  "products": product_data
                              }}, upsert=True)


def add_product_data(telegram_id, products_array):
    users.find_one_and_update({"telegram_id": telegram_id},
                              {"$set": {
                                  "products": products_array
                              }}, upsert=True)


def products_field_exists(telegram_id):
    query = users.find({
        '$and': [
            {'telegram_id': telegram_id},
            {'products': {'$exists': True}}
        ]
    })

    for result in query:
        if (result is not None):
            return True

    return False


def get_size_of_products_array(telegram_id):
    if (products_field_exists(telegram_id)):
        return_data = users.aggregate([
            {'$match': {'telegram_id': telegram_id}},
            {'$project': {
                'count': {'$size': '$products'}
            }
            }
        ])
        for result in return_data:
            return result['count']
    return 0
