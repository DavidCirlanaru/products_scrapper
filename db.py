import pymongo
from pymongo import MongoClient

# Database init
client = MongoClient()
product_link_list = []
client = MongoClient('mongodb://localhost:27017')
db = client.emag_scrapper
users = db.users


def add_user(name, urls):
    query = users.find_one({"name": name})
    if (query is not None):
        users.find_one_and_update({"name": name},
                                  {"$set": {"urls": urls}})
        return

    user_data = {
        'name': name,
        'urls': urls
    }
    users.insert_one(user_data)


def list_user(name):
    query = users.find_one({"name": name})
    if (query is not None):
        return query
    print('Not found')


def delete_link(name, index):
    query = users.find_one({"name": name})
    if (query is not None):
        users.update_one(
            {'name': name}, {'$unset': {f'urls.{index}': 1}})
        users.update_one({'name': name}, {'$pull': {'urls': None}})
