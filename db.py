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
        users.find_one_and_update({"name": name},  {"$set": {"urls": urls}})
        return

    user_data = {
        'name': name,
        'urls': urls
    }
    result = users.insert_one(user_data)
    return result


def list_user(name):
    query = users.find_one({"name": name})
    if (query is not None):
        return query
    print('Not found')


# def delete_link(name, index):

    # delete_link('Liviu', 1)
