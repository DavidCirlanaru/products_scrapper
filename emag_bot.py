from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, InlineQueryHandler, CallbackContext
from telegram import InlineQueryResultArticle, InputTextMessageContent
import re
import requests
import os
import sys
from threading import Thread
import db


# Vars
product_link_list = []

# Functions


def format_url(url):
    if(url.find('?') != -1):
        formated_url = remove_command_prefix(url)
        return formated_url.split('?', 1)[0]
    return url.strip('/add ')


def remove_command_prefix(string):
    return re.sub(r'(?=/)(.*)(\s)', '', string)

# Main


def main():
    updater = Updater(
        token="974325358:AAHMadWgjB59AARPGo95_ASE_ORoPspATLk",  use_context=True)
    dispatcher = updater.dispatcher

    def add(update, context):
        chat_id = update.effective_chat.id
        url = format_url(update.message.text)
        if (url in product_link_list):
            context.bot.send_message(
                chat_id, text='The link is already in the list.')
            return
        if(len(product_link_list) >= 10):
            context.bot.send_message(
                chat_id, text='Exceeded the maximum number of links in the list.')
            return
        product_link_list.append(url)
        context.bot.send_message(chat_id, text='Link added.')
        print(product_link_list)

    def delete(update, context):
        chat_id = update.effective_chat.id
        index_to_remove = remove_command_prefix(update.message.text)
        index_to_remove = int(index_to_remove)
        if (index_to_remove > 0 and index_to_remove <= 11 and product_link_list is not []):
            context.bot.send_message(
                chat_id, text='Deleting link number ' + str(index_to_remove) + '..')
            del product_link_list[int(index_to_remove) - 1]
            print(product_link_list)
            context.bot.send_message(
                chat_id, text='Deleted succesfuly.')
            return product_link_list
        else:
            context.bot.send_message(
                chat_id, text='Invalid request. Please try a different link number')
            return

    def links_list(update, context):
        chat_id = update.effective_chat.id
        if len(product_link_list) == 0:
            context.bot.send_message(
                chat_id, text='The list is empty.')
            return

        index = 1
        for link in product_link_list:
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


if __name__ == '__main__':
    main()
