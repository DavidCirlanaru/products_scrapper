# import secrets
# import requests
# import json
# import os


# # When user initializes the chat
# # I get this json
# # {
# #     ok: true,
# #     result: [
# #         {
# #             update_id: 311242598,
# #             message: {
# #                 message_id: 18,
# #                 from: {
# #                     id: 715166577,
# #                     is_bot: false,
# #                     first_name: "Dave",
# #                     last_name: "C",
# #                     language_code: "en"
# #                 },
# #                 chat: {
# #                     id: 715166577,
# #                     first_name: "Dave",
# #                     last_name: "C",
# #                     type: "private"
# #                 },
# #                 date: 1574800557,
# #                 text: "hi"
# #             }
# #         }
# #     ]
# # }

# # random_token = secrets.token_urlsafe(8)
# # https://api.telegram.org/bot974325358:AAHMadWgjB59AARPGo95_ASE_ORoPspATLk/getUpdates

# telegram_url = 'https://www.telegram.me'
# bot_name = 'emag_scrapper_bot'
# # token = random_token
# # url = f'{telegram_url}/{bot_name}?start={token}'

# bot_token = '974325358:AAHMadWgjB59AARPGo95_ASE_ORoPspATLk'
# # => '/start uEDbtJFHxKc'splitted_text = text.split(' ')# => ['/start', 'uEDbtJFHxKc']token = splitted_text[-1]# => 'uEDbtJFHxKc'
# updates_url = f'https://api.telegram.org/bot{bot_token}/getUpdates'
# response = requests.get(updates_url).json()

# splitted_text = text.split(' ')

# connect_token = splitted_text[-1]


# liviu_chat_id = '358903325'
# david_chat_id = '715166577'
# bot_key = connect_token
# external_link = 'https://www.pornhub.com/'
# notification_text = f'A aparut reducere la pula, grabeste-te liviu click aici --> {external_link}'
# send_message_url = f'https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={david_chat_id}&text={notification_text}&parse_mode=markdown'
# requests.post(send_message_url)
