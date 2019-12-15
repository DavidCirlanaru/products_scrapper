from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from validators import validate_url, domain_validate_url
import re
import os
import sys
from threading import Thread
import db
import config

# Functions


def format_url(url):
    url.strip()
    if(url.find('?') != -1):
        formated_url = remove_command_prefix(url)
        return formated_url.split('?', 1)[0]
    return url.strip('/add ')


def remove_command_prefix(string):
    return re.sub(r'(?=/)(.*)(\s)', '', string)


updater = Updater(
    token=config.bot_token,  use_context=True)
dispatcher = updater.dispatcher


def add(update, context):
    chat_id = update.effective_chat.id
    chat_data = context.bot.getChat(update.message.chat_id)
    current_user = chat_data['username']
    db_user = db.list_user(current_user)
    if (db_user is not None):
        product_links_list = db_user['urls']
    else:
        product_links_list = []
    print(product_links_list)
    url = format_url(update.message.text)

    if (validate_url(url) is True and domain_validate_url('www.emag.ro', url)):
        if (url in product_links_list):
            context.bot.send_message(
                chat_id, text='The link is already in the list.')
            return

        if(len(product_links_list) >= 10):
            context.bot.send_message(
                chat_id, text='Exceeded the maximum number of links in the list.')
            return

        # Add the link
        product_links_list.append(url)
        db.add_user(current_user, product_links_list, chat_id)
        context.bot.send_message(chat_id, text='Link added.')
        print(product_links_list)
    else:
        context.bot.send_message(
            chat_id, text='URL not valid, please try again.')


def delete(update, context):
    chat_id = update.effective_chat.id
    chat_data = context.bot.getChat(update.message.chat_id)
    current_user = chat_data['username']
    db_user = db.list_user(current_user)
    product_links_list = db_user['urls']

    index_to_remove = remove_command_prefix(update.message.text)
    index_to_remove = int(index_to_remove)
    index = index_to_remove - 1
    if (index_to_remove > 0 and index_to_remove <= 11 and product_links_list is not []):
        try:
            context.bot.send_message(
                chat_id, text='Deleting product ' + str(index_to_remove))

            # del product_links_list[int(index_to_remove) - 1]
            db.delete_link(current_user, index)
            print(product_links_list)
            context.bot.send_message(
                chat_id, text=f'Deleted {product_links_list[index]}')
            return product_links_list
        except IndexError:
            context.bot.send_message(
                chat_id, text=f'No product with number {index_to_remove} found.')

    else:
        context.bot.send_message(
            chat_id, text='Invalid request. Please try a different link number.')
        return


def links_list(update, context):
    chat_id = update.effective_chat.id
    chat_data = context.bot.getChat(update.message.chat_id)
    current_user = chat_data['username']
    db_user = db.list_user(current_user)
    product_links_list = db_user['urls']

    if len(product_links_list) == 0:
        context.bot.send_message(
            chat_id, text='The list is empty.')
        return

    index = 1
    for link in product_links_list:
        print(link)
        context.bot.send_message(chat_id, text=str(index)+"| " + link)
        index += 1


def unknown(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Sorry, I didn't understand that command..")


def stop_and_restart():
    """Stop the Updater and replace the current process with a new one"""
    updater.stop()
    os.execl(sys.executable, sys.executable, *sys.argv)


def restart(update, context):
    update.message.reply_text('Bot is restarting...')
    Thread(target=stop_and_restart).start()
    update.message.reply_text('Bot started...')


# Handlers
dispatcher.add_handler(CommandHandler(
    'r', restart, filters=Filters.user(username='@DaveC97')))

add_link_handler = CommandHandler('add', add)
dispatcher.add_handler(add_link_handler)

delete_link_handler = CommandHandler('delete', delete)
dispatcher.add_handler(delete_link_handler)

list_handler = CommandHandler('list', links_list)
dispatcher.add_handler(list_handler)

# Keep this as last
unknown_handler = MessageHandler(Filters.command, unknown)
dispatcher.add_handler(unknown_handler)

updater.start_polling()
print('Started polling..')
updater.idle()
