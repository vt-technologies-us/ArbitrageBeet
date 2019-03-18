from telegram import ParseMode
from telegram.ext import Updater, CommandHandler

import arbitrage
import basics


def start(bot, update):
    user = update.message.chat_id
    with open('messages/welcome.txt') as f:
        msg = '\n'.join(f.readlines())
    msg = msg.format(name=' '.join([update.message.chat.first_name, update.message.chat.last_name]))
    bot.sendMessage(chat_id=user, text=msg)

    with open('messages/disclaimer.txt') as f:
        msg = '\n'.join(f.readlines())
    bot.sendMessage(chat_id=user, text=msg)


def request(bot, update):
    def sender(msg):
        user = update.message.chat_id
        bot.sendMessage(chat_id=user, text=f'```\n{msg}\n```', parse_mode=ParseMode.MARKDOWN)

    arbitrage.find_arbitrage(sender)


if __name__ == '__main__':
    updater = Updater(token=basics.secrets['telegram'])

    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CommandHandler('request', request))

    updater.start_polling()
    updater.idle()
