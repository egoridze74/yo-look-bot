from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler
)
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, User, InputMediaPhoto
from secret import Token
from constants import *
import logging


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


USER_PATHS = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.message.from_user
    logger.info("User %s started the conversation.", user.first_name)
    await update.message.reply_text(Messages.start_message)


async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = []
    for ex in Excursions.excursions:
        keyboard.append([InlineKeyboardButton(Excursions.excursions[ex].get("name"),
                        callback_data=Excursions.excursions[ex].get("keyboard_callback"))])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.effective_user.send_message(text='Выберите экскурсию:', reply_markup=reply_markup)


async def path_format(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = TelegramFeatures.format_keyboard
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.effective_user.send_message(text='Выберите формат экскурсии:', reply_markup=reply_markup)


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    if query.data == "PATH_STAGE":
        await menu(update, context)
    elif query.data == "FORMAT_STAGE":
        await path_format(update, context)
    elif "PATH" in query.data:
        USER_PATHS[query.from_user["id"]] = query.data
        await path_format(update, context)
    elif query.data == "TEXT":
        await send_text_excursion(query.from_user, update, context)
    elif query.data == "AUDIO":
        pass
    elif query.data == "VIDEO":
        pass


async def info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(Messages.info_message)


async def send_text_excursion(user: User, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    exc = Excursions.excursions[USER_PATHS[user["id"]]]
    await user.send_photo(open(exc["path_map"], "rb"), f"Вот карта этого маршрута.\n\n"
                                                            f"Длина: {exc["length"]}\n\n"
                                                            f"Продолжительность: {exc["time"]}\n\n"
                                                            f"Вайб маршрута:\n{exc["description"]}")
    for landmark in exc["landmarks"].values():
        await user.send_photo(open(landmark["photo"], "rb"), landmark["name"])
        await user.send_message(landmark["text"])
    await user.send_message(exc["final_message"])
    keyboard = TelegramFeatures.back_to_format_keyboard
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.effective_user.send_message(text="Хотите вернуться к форматам этой экскурсии?", reply_markup=reply_markup)


def main():
    application = Application.builder().token(Token.token).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("menu", menu))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(CommandHandler("info", info))
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
