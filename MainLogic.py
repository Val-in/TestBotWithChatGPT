import telebot.types
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from dotenv import load_dotenv
import os
from openai import OpenAI


# load_dotenv() 
bot_token = os.getenv("TELEGRAM_TOKEN")
openai_key = os.getenv("OPENAI_API_KEY")
GPT_URL = "https://api.openai.com/v1/chat/completions"

bot = telebot.TeleBot(bot_token)

user_dict = {}
client = OpenAI(api_key=openai_key)

def reset_context(user_id):
    user_dict[user_id] = []


def add_message(user_id, role, content):
    if user_id not in user_dict:
        reset_context(user_id)
    user_dict[user_id].append({"role": role, "content": content})


def send_to_gpt(messages):
    try:
        completion = client.chat.completions.create(
            model="gpt-5.1",
            messages=messages
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Ошибка при обращении к ChatGPT: {e}"

@bot.message_handler(commands=['start'])
def start(message):
        user_id = message.chat.id
        reset_context(user_id)

        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(KeyboardButton("Новый запрос"))
        markup.add(KeyboardButton("Помощь"))

        bot.send_message(user_id,
                     "Привет! Я бот на основе ChatGPT.\nНапиши, что хочешь узнать, и я отвечу 😉",
                     reply_markup=markup)


@bot.message_handler(commands=['help'])
def show_help(message):
    bot.send_message(message.chat.id,
                     "У меня есть такие команды:\n/start — cпросить что-нибудь\n/help — получить помощь")


@bot.message_handler(func=lambda msg: msg.text in ["Новый запрос", "Помощь"])
def handle_buttons(message):
    user_id = message.chat.id
    if message.text == "Новый запрос":
        reset_context(user_id)
        bot.send_message(user_id, "История очищена. Пиши новый запрос 👇")
    elif message.text == "Помощь":
        show_help(message)

@bot.message_handler(content_types=['text'])
def chat(message):
    user_id = message.chat.id
    text = message.text

    add_message(user_id, "user", text)

    answer = send_to_gpt(user_dict[user_id])
    add_message(user_id, "assistant", answer)

    bot.send_message(user_id, answer)

print("Bot started")
bot.infinity_polling()
