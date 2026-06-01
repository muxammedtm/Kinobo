import logging, sys, os
sys.path.insert(0, os.path.dirname(__file__))

from telegram import Update
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, filters
)
from config import Config
from database import Database
from handlers.user import cmd_start, cb_lang, cb_check_sub, handle_text, cb_favorite
from handlers.admin import cmd_admin, admin_callback, admin_state_handler
from referral_handler import cmd_ref, ref_callback, ref_state_handler

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO,
    handlers=[
        logging.FileHandler("bot.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

cfg = Config()
db  = Database(cfg.DB_PATH)


async def universal_handler(update, context):
    user = update.effective_user
    if not user:
        return

    # 1. Referral state
    if await ref_state_handler(update, context):
        return

    # 2. Admin state
    if user.id == cfg.OWNER_ID or user.id in db.get_admin_ids():
        if await admin_state_handler(update, context):
            return

    # 3. Oddiy foydalanuvchi
    await handle_text(update, context)


def main():
    logger.info("🚀 Bot ishga tushmoqda...")
    app = Application.builder().token(cfg.BOT_TOKEN).build()

    # Buyruqlar
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("admin", cmd_admin))
    app.add_handler(CommandHandler("ref",   cmd_ref))

    # Callbacklar — tartib muhim!
    app.add_handler(CallbackQueryHandler(cb_lang,       pattern=r"^lang_"))
    app.add_handler(CallbackQueryHandler(cb_check_sub,  pattern=r"^check_sub$"))
    app.add_handler(CallbackQueryHandler(cb_favorite,   pattern=r"^fav_"))
    app.add_handler(CallbackQueryHandler(ref_callback,  pattern=r"^ref_"))
    app.add_handler(CallbackQueryHandler(admin_callback))

    # Xabarlar
    app.add_handler(MessageHandler(
        filters.TEXT | filters.VIDEO | filters.Document.ALL | filters.PHOTO,
        universal_handler
    ))

    logger.info("✅ Bot ishga tushdi!")
    app.run_polling(drop_pending_updates=True, allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
