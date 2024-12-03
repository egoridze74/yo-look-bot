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


USER_PATHS_AND_LANDMARKS = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.message.from_user
    logger.info("User %s started the conversation.", user.first_name)
    await update.message.reply_text(Messages.start_message, parse_mode="MarkdownV2")


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
    elif query.data == "NEXT_TEXT":
        USER_PATHS_AND_LANDMARKS[query.from_user["id"]][1] += 1
        await send_text_excursion(query.from_user, update, context)
    elif query.data == "NEXT_AUDIO":
        USER_PATHS_AND_LANDMARKS[query.from_user["id"]][1] += 1
        await send_audio_excursion(query.from_user, update, context)
    elif "PATH" in query.data:
        USER_PATHS_AND_LANDMARKS[query.from_user["id"]] = ["", 0]
        USER_PATHS_AND_LANDMARKS[query.from_user["id"]][0] = query.data
        await path_format(update, context)
    elif query.data == "TEXT":
        await send_text_excursion(query.from_user, update, context)
    elif query.data == "AUDIO":
        await send_audio_excursion(query.from_user, update, context)
    elif query.data == "VIDEO":
        await send_video_excursion(query.from_user, update, context)


async def info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(Messages.info_message, parse_mode="MarkdownV2")


async def send_text_excursion(user: User, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    exc = Excursions.excursions.get(USER_PATHS_AND_LANDMARKS[user["id"]][0])
    land_count = USER_PATHS_AND_LANDMARKS[user["id"]][1]
    cur_landmarks = list(exc.get("landmarks").values())
    if land_count == 0:
        await user.send_photo(open(exc["path_map"], "rb"), f"Вот карта этого маршрута\.\n\n"
                                                           f"*Длина:* {exc.get("length")}\n\n"
                                                           f"*Продолжительность:* {exc.get("time")}\n\n"
                                                           f"{exc.get("music")}\n\n"
                                                           f"*Вайб маршрута:*\n{exc.get("description")}",
                                                            parse_mode="MarkdownV2")
        await user.send_message(text="Посмотрим первую достопримечательность?",
                                reply_markup=InlineKeyboardMarkup(TelegramFeatures.next_text_keyboard))
    else:
        if cur_landmarks[land_count - 1]["name"] != "cafe":
            await user.send_photo(open(cur_landmarks[land_count - 1].get("photo"), "rb"),
                                  f"*{cur_landmarks[land_count - 1].get("name")}*", parse_mode="MarkdownV2")
        await user.send_message(cur_landmarks[land_count - 1].get("text"), parse_mode="MarkdownV2")
        if land_count < len(cur_landmarks):
            await user.send_message(text="Посмотрим следующую достопримечательность?",
                                    reply_markup=InlineKeyboardMarkup(TelegramFeatures.next_text_keyboard))
        else:
            await user.send_message(exc.get("final_message"), parse_mode="MarkdownV2")
            USER_PATHS_AND_LANDMARKS[user["id"]][1] = 0
            keyboard = TelegramFeatures.back_to_format_keyboard
            await update.effective_user.send_message(text="Хотите вернуться к форматам этой экскурсии?",
                                                     reply_markup=InlineKeyboardMarkup(keyboard))


async def send_audio_excursion(user: User, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    exc = Excursions.excursions.get(USER_PATHS_AND_LANDMARKS[user["id"]][0])
    land_count = USER_PATHS_AND_LANDMARKS[user["id"]][1]
    cur_landmarks = list(exc.get("landmarks").values())
    if land_count == 0:
        await user.send_photo(open(exc["path_map"], "rb"), f"Вот карта этого маршрута\.\n\n"
                                                           f"*Длина:* {exc.get("length")}\n\n"
                                                           f"*Продолжительность:* {exc.get("time")}\n\n"
                                                           f"{exc.get("music")}\n\n"
                                                           f"*Вайб маршрута:*\n{exc.get("description")}\n\n"
                                                           f"Слушая нашу экскурсию, будьте осторожны и "
                                                                         "не забывайте смотреть по сторонам\!",
                                                            parse_mode="MarkdownV2")
        await user.send_message(text="Послушаем про первую достопримечательность?",
                                reply_markup=InlineKeyboardMarkup(TelegramFeatures.next_audio_keyboard))
    else:
        if cur_landmarks[land_count - 1]["name"] != "cafe":
            await user.send_audio(open(cur_landmarks[land_count - 1].get("audio_file"), "rb"))
        else:
            await user.send_message(cur_landmarks[land_count - 1].get("text"), parse_mode="MarkdownV2")
        if land_count < len(cur_landmarks):
            await user.send_message(text="Послушаем про следующую достопримечательность?",
                                    reply_markup=InlineKeyboardMarkup(TelegramFeatures.next_audio_keyboard))
        else:
            await user.send_message(exc.get("final_message"), parse_mode="MarkdownV2")
            USER_PATHS_AND_LANDMARKS[user["id"]][1] = 0
            keyboard = TelegramFeatures.back_to_format_keyboard
            await update.effective_user.send_message(text="Хотите вернуться к форматам этой экскурсии?",
                                                     reply_markup=InlineKeyboardMarkup(keyboard))


async def send_video_excursion(user: User, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    exc = Excursions.excursions.get(USER_PATHS_AND_LANDMARKS[user["id"]][0])
    if exc.get("video_file"):
        await user.send_video(open(exc.get("video_file"), "rb"))
    keyboard = TelegramFeatures.back_to_format_keyboard
    await update.effective_user.send_message(text="Хотите вернуться к форматам этой экскурсии?",
                                             reply_markup=InlineKeyboardMarkup(keyboard))


def main():
    application = (Application.builder().token(Token.token)
                    .read_timeout(30)
                    .write_timeout(30).build())
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("menu", menu))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(CommandHandler("info", info))
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
