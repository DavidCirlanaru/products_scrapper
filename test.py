import db

users = db.get_all_users()

for user in users:
    print(user['username'])
    print(user['urls'])
# for each user get all ther urls.
# la fiecare x minute
# treci prin toate linkurile din baza de date,
# scrape
# creaza un array de obiecte pentru fiecare URL si pune-l la fiecare user
