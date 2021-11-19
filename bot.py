import time
import logging
from sqlalchemy.sql.expression import text
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
)
from telegram import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove,error
from os import environ
from database import (
    SESSION,
    Users,
    add_attribute_to_user,
    check_is_disqalified,
    check_is_finished,
    check_user_exists,
    create_new_user,
    get_user,
)
from functions import check_status, get_balance, get_transaction_date
import random

JOIN, PHOTO, ADRESS, TXN = range(4)
SUDO_USERS = [1609835380, 1911773885]

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)


def start(update, context):
    keyboard = ReplyKeyboardMarkup(
        ([[KeyboardButton("Join")], [KeyboardButton("Cancel")]]), resize_keyboard=True
    )
    admin_keyboard = ReplyKeyboardMarkup(
        ([[KeyboardButton("Start The Draw")]]), resize_keyboard=True
    )
    text = """🔥🔥🚀Nasadoge Family🚀🔥🔥 Our iPhone XR (128Gb) award-winning event, which you can take part  until the end of this month (30/11/2021), starts. Conditions to participate in the draw; 

▪️You will win 1 (one) lottery right for the purchase of Nasadoge with a minimum value of 35000 Nasadoge Token to your current wallet or a new wallet at once. You can participate with more wallets and increase your luck. . 

▪️If you keep the Nasadoge tokens you have received in your wallet for a minimum of 15 days, you will be entitled to participate in the draw. Example 1: You bought Nasadoge on 20/11/2021 and did not sell it until 05/12/2021, you are eligible for the draw on the 15th of the month. Example 2: You bought Nasadoge on 16/11/2021 and did not sell it until 01/12/2021, you are eligible for the draw on the 15th of the month. 

▪️To participate in the campaign, your purchases must be on pancakeswap, purchases on the stock market are not included in the campaign, as wallets cannot be followed. 

▪️After purchasing, you need to add the Metamask or Trust wallet screenshot, your Nasadoge wallet address, txn hash from bscscan (Not link, only hash code) to the Nasadoge activity bot and participate in the campaign. 

▪️The results of the draw will be determined in the presence of you by opening a live broadcast on the group on the 15th of December. 

▪️Admin and administrators are not included in the campaign. 

NOTE: Participation in the campaign will start from 16/11/2021 00:00.
"""
    bot = context.bot
    user = update.effective_user
    chat = update.effective_chat
    message = update.effective_message
    if chat.type == "private":
        if user.id in SUDO_USERS:
            bot.send_message(
                chat.id,
                "Admin Menu",
                reply_markup=admin_keyboard,
                parse_mode="MARKDOWN",
            )
            return ConversationHandler.END
        if not check_user_exists(user.id):
            create_new_user(user.id, user.username)
            if not check_is_finished(user.id) or not check_is_disqalified(user.id):
                bot.send_message(
                    chat.id, text, reply_markup=keyboard, parse_mode="MARKDOWN"
                )
                return JOIN
            else:
                message.reply_text("You already joined!")
                return ConversationHandler.END
        else:
            message.reply_text("You already joined!")
            return ConversationHandler.END


def join(update, context):
    bot = context.bot
    user = update.effective_user
    chat = update.effective_chat
    message = update.effective_message
    if chat.type == "private":
        message.reply_text(
            "Send screenshot of trust wallet or metamask with NasaDoge token balance",
            reply_markup=ReplyKeyboardRemove(),
        )
        return PHOTO
    else:
        return ConversationHandler.END


def photo(update, context, returns=False):
    global DATA
    bot = context.bot
    user = update.effective_user
    chat = update.effective_chat
    message = update.effective_message
    if chat.type == "private":
        if returns:
            bot.send_message(
                chat_id=chat.id, text=f"Enter the bep20 address you purchased from"
            )
            return ADRESS
        photo_id = message.photo[0].file_id
        add_attribute_to_user(user.id, "photo_id", photo_id)
        bot.send_message(
            chat_id=chat.id, text=f"Enter the bep20 address you purchased from"
        )
        return ADRESS


def adress(update, context, returns=False):
    bot = context.bot
    user = update.effective_user
    chat = update.effective_chat
    message = update.effective_message
    adress = message.text
    if chat.type == "private":
        if returns:
            message.reply_text(f"Send purchase txn hash from bscscan")
            return TXN
        while True:
            if get_balance(adress) == "no nasadoge":
                message.reply_text(
                    "There is no Nasa Doge token at this address, please send the address where you bought the Nasadoge token"
                )
                return photo(update, context, returns=True)
            if get_balance(adress) == "wrong_adress":
                message.reply_text(
                    "This address is not true, please send correct bep20 address"
                )
                return photo(update, context, returns=True)
            if get_balance(adress) != None:
                if int(get_balance(adress)[:-9]) < 350000:
                    message.reply_text(
                        "Your balance is not enough to participate in the lottery! Min Balance: 350000 Nasadoge Token"
                    )
                    return photo(update, context, returns=True)
                if SESSION.query(Users).filter_by(adress=adress).first():
                    message.reply_text("This address already used!!!")
                    return photo(update, context, returns=True)
                raw_balance = get_balance(adress)
                readable_balance = format(int(raw_balance[:-9]), ",")
                after_dot = raw_balance[-9:]
                add_attribute_to_user(user.id, "adress", adress)
                add_attribute_to_user(user.id, "raw_balance", raw_balance)
                add_attribute_to_user(
                    user.id, "readable_balance", str(readable_balance + "." + after_dot)
                )
                message.reply_text(
                    f"Nasadoge Balance of this adress {str(readable_balance)}.{str(after_dot)}"
                )
                message.reply_text(f"Send purchase txn hash from bscscan")
                return TXN
            else:
                message.reply_text(
                    "Error getting address, please try again, if error continue, please contact admin"
                )
                continue


def txn(update, context):
    keyboard = ReplyKeyboardMarkup(
        ([[KeyboardButton("Profile")]]), resize_keyboard=True
    )
    bot = context.bot
    user = update.effective_user
    chat = update.effective_chat
    message = update.effective_message
    txn = message.text
    if chat.type == "private":
        while True:
            if SESSION.query(Users).filter_by(txn=txn).first():
                message.reply_text("This txn already used!!!")
                return adress(update, context, returns=True)
            transaction_date = str(get_transaction_date(txn))
            add_attribute_to_user(user.id, "txn", txn)
            add_attribute_to_user(user.id, "transaction_date", transaction_date)
            add_attribute_to_user(user.id, "finish")
            message.reply_text("You joined sweepstake", reply_markup=keyboard)
            send_admin(bot, user.id)
            return ConversationHandler.END


def send_admin(bot, userid):
    chat_id = "-1001676896058"
    user = get_user(userid)
    text = """
*New User joined*

- *Username*: `{}`
- *Userid*: `{}`
- *Bep20*: `{}`
- *Balance*: `{}`
- *Txn*: `{}`
- *Transaction Date*: `{}`
    """.format(
        user.username,
        user.userid,
        user.adress,
        user.readable_balance,
        user.txn,
        user.transaction_date,
    )
    bot.send_photo(chat_id, photo=user.photo_id, caption=text, parse_mode="MARKDOWN")


def profile(update, context):
    bot = context.bot
    user = update.effective_user
    chat = update.effective_chat
    message = update.effective_message
    txn = message.text
    if chat.type == "private":
        user = get_user(user.id)
        text = """
*Username*: `{}`
*UserID*: `{}`
*Bep20:* `{}`
*Nasadoge Balance*: `{}`
        """.format(
            user.username, user.userid, user.adress, user.readable_balance
        )
        message.reply_text(text, parse_mode="MARKDOWN")


def cancel(update, context):
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text(
        "Bye! I hope we can talk again some day.", reply_markup=ReplyKeyboardRemove()
    )


def random_select(update, context):
    user = update.effective_user
    chat = update.effective_chat
    if chat.type == "private":
        if user.id in SUDO_USERS:
            username_liste = []
            user_id_liste = []
            users = SESSION.query(Users).all()
            sent = context.bot.send_message(chat.id, text='Drawing: ', parse_mode="HTML")
            for i in users:
                if not i.is_disqalified:
                    username_liste.append(i.username)
                    user_id_liste.append(i.userid)
            for username,userid in zip(username_liste,user_id_liste):
                user = random.choice(username_liste)
                try:
                    context.bot.edit_message_text(chat_id = chat.id, message_id = sent.message_id,text=f'Drawing: {user}', parse_mode="HTML")
                except error.BadRequest:
                    pass
                except error.RetryAfter:
                    if "This user has no username" in user:
                        return context.bot.edit_message_text(chat_id = chat.id, message_id = sent.message_id, text=f'Winner: {user}', parse_mode="HTML")
                    return context.bot.edit_message_text(chat_id = chat.id, message_id = sent.message_id, text=f'Winner: <a href="https://t.me/{user}">{user}</a>', parse_mode="HTML")
                except error.TimedOut:
                    if "This user has no username" in user:
                        return context.bot.edit_message_text(chat_id = chat.id, message_id = sent.message_id, text=f'Winner: {user}', parse_mode="HTML")
                    return context.bot.edit_message_text(chat_id = chat.id, message_id = sent.message_id, text=f'Winner: <a href="https://t.me/{user}">{user}</a>', parse_mode="HTML")
            random.shuffle(username_liste)
            random.shuffle(username_liste)
            user = random.choice(username_liste)
            if "This user has no username" in user:
                return context.bot.edit_message_text(chat_id = chat.id, message_id = sent.message_id, text=f'Winner: {user}', parse_mode="HTML")
            context.bot.edit_message_text(chat_id = chat.id, message_id = sent.message_id, text=f'Winner: <a href="https://t.me/{user}">{user}</a>', parse_mode="HTML")
        return


def diskalifiye(update, context):
    while True:
        check_status()
        time.sleep(86400)


def main():
    updater = Updater(token="2106948693:AAH5fwRSndVNvdCUW5HRQGz93gKKi3mLyNQ", workers=4)
    dispatcher = updater.dispatcher
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            JOIN: [MessageHandler(Filters.regex("Join"), join)],
            PHOTO: [MessageHandler(Filters.photo, photo)],
            ADRESS: [MessageHandler(Filters.text & ~Filters.command, adress)],
            TXN: [MessageHandler(Filters.text & ~Filters.command, txn)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    dispatcher.add_handler(conv_handler)
    dispatcher.add_handler(
        MessageHandler(Filters.regex("Profile"), profile, run_async=True)
    )
    dispatcher.add_handler(
        MessageHandler(Filters.regex("Start The Draw"), random_select, run_async=True)
    )
    dispatcher.add_handler(CommandHandler("diskalifiye", diskalifiye, run_async=True))
    updater.start_polling(timeout=2000)
    updater.idle()


if __name__ == "__main__":
    main()
