import telebot
from telethon.tl.types import Chat

bot = telebot.TeleBot('2135853784:AAE502f7WW21IZ_Z5Pp3feP9ArdM6FmuObQ')


def send_text(message):
    bot.send_message(369434053, message)


send_text('testttt')

bot.polling(none_stop=True)
