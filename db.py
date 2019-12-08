import pymongo
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


def add_user(name, urls):
    query = users.find_one({"name": name})
    if (query is not None):
        users.find_one_and_update({"name": name},
                                  {"$set": {"urls": urls}}, upsert=True)
        return

    user_data = {
        'name': name,
        'urls': urls
    }
    result = users.insert_one(user_data)
    print(format(result.inserted_id))


def list_user(name):
    query = users.find_one({"name": name})
    if (query is not None):
        return query
    print('Could not find the user with that name.')


def delete_link(name, index):
    query = users.find_one({"name": name})
    if (query is not None):
        users.update_one(
            {'name': name}, {'$unset': {f'urls.{index}': 1}})
        users.update_one({'name': name}, {'$pull': {'urls': None}})

# def add_product_data(name, product_data):
