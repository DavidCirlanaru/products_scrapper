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


def get_chat_id(username):
    query = users.find_one({"username": username})
    if (query is not None):
        return query['chat_id']
    print('Could not find the user with that username.')


def add_user(username, urls, chat_id):
    query = users.find_one({"username": username})
    if (query is not None):
        users.find_one_and_update({"username": username},
                                  {"$set": {"urls": urls}}, upsert=True)
        return

    user_data = {
        'username': username,
        'chat_id': chat_id,
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


def overwrite_product_data(username, product_data):
    users.find_one_and_update({"username": username},
                              {"$set": {
                                  "products": product_data
                              }}, upsert=True)


def add_product_data(username, product_data):
    if (products_field_exists(username) is True):
        users.find_one_and_update({"username": username},
                                  {"$addToSet": {
                                      "products":
                                      {
                                          'title': product_data['title'],
                                          'original_price': product_data['original_price'],
                                          'number_of_resealed_products': product_data['number_of_resealed_products'],
                                          'array_of_resealed_prices': product_data['array_of_resealed_prices'],
                                          'product_url': product_data['product_url']
                                      }
                                  }}, upsert=True)
    else:
        users.find_one_and_update({"username": username},
                                  {"$push": {
                                      "products":
                                      {
                                          'title': product_data['title'],
                                          'original_price': product_data['original_price'],
                                          'number_of_resealed_products': product_data['number_of_resealed_products'],
                                          'array_of_resealed_prices': product_data['array_of_resealed_prices'],
                                          'product_url': product_data['product_url']
                                      }
                                  }}, upsert=True)


def products_field_exists(username):
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


def get_size_of_products_array(username):
    if (products_field_exists(username)):
        return_data = users.aggregate([
            {'$match': {'username': username}},
            {'$project': {
                'count': {'$size': '$products'}
            }
            }
        ])
        for result in return_data:
            return result['count']
    return 0
