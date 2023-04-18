from cards.tarot import deck
from opencc import OpenCC
import openai, configparser, logging
from flask import Flask, request, Response
from telegram import Bot, InlineKeyboardMarkup, InlineKeyboardButton, Update
from telegram.ext import Dispatcher, MessageHandler, Filters, CallbackContext, Updater
import random

config = configparser.ConfigParser()
config.read("config.ini")

# to traditional chinese
cc = OpenCC("s2hk")

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

logger = logging.getLogger(__name__)

openai.api_key = config["OPENAI"]["ACCESS_TOKEN"]
API_KEY = config["TELEGRAM"]["ACCESS_TOKEN"]
bot = Bot(API_KEY)
dispatcher = Dispatcher(bot, None)

app = Flask(__name__)


temp = dict()
area = "健康"


@app.route("/hook", methods=["POST"])
def webhook_handler():
    if request.method == "POST":
        update = Update.de_json(request.get_json(force=True), bot)
        dispatcher.process_update(update)
        return Response("ok", status=200)


def reply_handler(update: Update, context: CallbackContext):
    global temp, area
    text = update.message.text

    ran_context = [
        "開始抽牌前，集中精神想一想你現在需要指引的問題，或是現正困擾你的生活狀況。你的精神愈集中，塔羅牌便能越有效的從你的心裡指引出清晰的道路。",
        "深呼吸一口氣，放鬆一下身體和心靈，協助內心清除雜念及放空自己，完全地靜下心來。如果你在一個嘈雜的環境的話，嘗試轉換到一個寧靜的環境，或是改變一個舒適的姿勢。",
        "請誠實接受塔羅牌給你的信息和指引，即使有些信息看來與你的想法大相徑庭，或許，這就是你需要的新角度。我們準備的解釋不一定完美反映你的狀況，卡牌的意思可能會帶給你不同的感覺，請嘗試把信息按你的感覺套用到你的生活中。",
        "塔羅牌的結果不是絕對，塔羅只能協助你看見事情的癥結，並給出一個指引。或者有些卡牌看似十分絕望，但不要害怕，卡牌只是反映最近的狀況，而且卡牌總會有正向的一面。",
        "絕對不要同一天反覆進行占卜，嘗試接受占卜得出的第一個結果吧！不停的占卜並不會為你帶來更清晰的指引，相反地，這樣做將只會令你更感迷惑。",
    ]

    user = update.message.from_user
    chat_id = user["id"]

    re = None

    if text[0] == "/":
        if text[1:6] == "tarot":
            # init deck
            temp[chat_id] = deck()
            temp[chat_id].shuffle()
            update.message.reply_text(f" /q 占卜範疇\n例如: /q 健康")
        if text[1:2] == "q":
            area = text[3:]
            logging.info(f"area: {area}")
            update.message.reply_text(f"{random.choice(ran_context)}\n然後以 /past 抽出代表過去的牌")
        elif text[1:5] == "past":
            temp[chat_id].past()
            update.message.reply_text(f"{random.choice(ran_context)}\n然後以 /now 抽出代表現在的牌")
        elif text[1:4] == "now":
            temp[chat_id].now()
            update.message.reply_text(f"{random.choice(ran_context)}\n然後以 /future 抽出代表未來的牌")
        elif text[1:7] == "future":
            temp[chat_id].future()
            update.message.reply_text(
                f"代表過去的牌:{temp[chat_id].table[0][0]} {temp[chat_id].table[0][1]}\n代表現在的牌:{temp[chat_id].table[1][0]} {temp[chat_id].table[1][1]}\n代表未來的牌:{temp[chat_id].table[2][0]} {temp[chat_id].table[2][1]}\n 以 /open 等待AI占卜結果"
            )
        elif text[1:5] == "open":
            re = ask(
                area,
                temp[chat_id].table[0],
                temp[chat_id].table[1],
                temp[chat_id].table[2],
            )
            logger.info(f"response: {re}")
            update.message.reply_text(re)

        elif text[1:5] == "test":
            update.message.reply_text(ask("人生", ["正位", "錢幣國王"], ["正位", "錢幣皇后"], ["正位", "錢幣騎士"]))

    else:
        update.message.reply_text("Command undefined")


def error(update, context):
    logging.info(f"Update {update} caused error {context.error}")
    update.message.reply_text("Something wrong, please try again later")


def ask(area: str, past: list, now: list, future: list) -> str:
    tarot_prompt = f"""
    假設你現在是一位塔羅牌占卜師，我已經抽了三張牌，分別代表過去，現在和未來，而我想作出關於{area}的占卜，其中代表過去的牌是{past[0]}的{past[1]}，代表現在的牌是{now[0]}的{now[1]}，代表未來的牌是{future[0]}的{future[1]}，請告訴我這三張牌分別是什麼意思，以及三張牌組合起來又是甚麼意思？"""
    logging.info(f"prompt: {tarot_prompt}")
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        # model="gpt-4",
        messages=[{"role": "user", "content": tarot_prompt}],
        # max_tokens=500
    )
    completed_text = cc.convert(response["choices"][0]["message"]["content"])
    logging.info(f"Res: {completed_text}")
    return completed_text


# def send(id, text):
#     url = f"https://api.telegram.org/bot{API_KEY}/sendMessage"
#     params = {
#         "chat_id": id,
#         "text": f"{text}",
#     }
#     resp = requests.get(url, params=params)

dispatcher.add_handler(MessageHandler(Filters.text, reply_handler))
dispatcher.add_error_handler(error)

if __name__ == "__main__":
    app.run(debug=True)
    # print("Bot started...")
    # updater = Updater(API_KEY, use_context=True)
    # dp = updater.dispatcher
    # dp.add_handler(MessageHandler(Filters.text, reply_handler))
    # updater.start_polling()
    # updater.idle()
