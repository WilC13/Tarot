from cards.tarot import deck
from opencc import OpenCC
import openai, logging, asyncio
from flask import Flask, request, make_response
from telegram import Bot, InlineKeyboardMarkup, InlineKeyboardButton, Update
from telegram.ext import (
    Dispatcher,
    MessageHandler,
    Filters,
    CallbackContext,
    CommandHandler,
)

# to traditional chinese
cc = OpenCC("s2hk")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)

openai.api_key = config["OPENAI"]["ACCESS_TOKEN"]
bot = Bot(config["TELEGRAM"]["ACCESS_TOKEN"])

dispatcher = Dispatcher(bot, None)

app = Flask(__name__)


@app.route("/hook", methods=["POST"])
async def webhook_handler():
    if request.method == "POST":
        update = Update.de_json(request.get_json(force=True), bot)

        response = make_response("This is a HTTP 200 OK response.", 200)
        await dispatcher.process_update(update)

    return response


# def reply_handler(update: Update, context: CallbackContext):
#     text = update.message.text
#     # update.message.reply_text("Processing")


#     user = update.message.from_user
#     user_id = user["id"]
async def tarot_gpt(update: Update, context: CallbackContext):
    text = update.message.text
    # update.message.reply_text("Processing")

    await update.message.reply_text(
        ask("人生", [["正位"], ["錢幣國王"]], [["逆位"], ["錢幣皇后"]], [["逆位"], ["錢幣騎士"]])
    )


def ask(area: str, past: list, now: list, future: list) -> str:
    tarot_prompt = f"""
    假設你現在是一位塔羅牌占卜師，我已經抽了三張牌，分別代表過去，現在和未來，而我想作出關於{area}的占卜，其中代表過去的牌是{past[0]}的{past[1]}，代表現在的牌是{now[0]}的{now[1]}，代表未的牌是{future[0]}的{future[1]}，請告訴我這三張牌分別是什麼意思，以及三張牌組合起來又是甚麼意思"""
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


async def main():
    dispatcher.add_handler(CommandHandler("tarot", tarot_gpt))
    app.run(debug=True)


if __name__ == "__main__":
    asyncio.run(main())
