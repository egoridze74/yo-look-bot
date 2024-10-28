from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from secret import Token
from constants import *


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(Messages.start_message)


async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = []
    for ex in Excursions.excursions:
        keyboard.append([InlineKeyboardButton(Excursions.excursions[ex].get("name"),
                                              callback_data=Excursions.excursions[ex].get("keyboard_callback"))])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Выберите экскурсию:', reply_markup=reply_markup)


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(text=f"Selected option: {query.data}")


def main():
    application = Application.builder().token(Token.token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(CommandHandler("menu", menu))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()