from telegram import Update
from telegram.ext import ContextTypes
from database import Database
from texts import t
from keyboards import lang_keyboard, main_menu, subscription_keyboard, movie_keyboard
from config import Config

db  = Database()
cfg = Config()


async def _check_sub(user_id, bot):
    if db.get_setting("sub_required") != "1":
        return []
    channels = db.get_channels()
    not_subbed = []
    for ch in channels:
        try:
            m = await bot.get_chat_member(ch["channel_id"], user_id)
            if m.status in ("left", "kicked", "banned"):
                not_subbed.append(ch)
        except Exception:
            not_subbed.append(ch)
    return not_subbed


def _lang(user_id):
    u = db.get_user(user_id)
    return u["lang"] if u else "uz"


# ─── /start ──────────────────────────────────────────────────────────────────

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user   = update.effective_user
    args   = context.args
    is_new = not db.get_user(user.id)

    if is_new:
        db.add_user(user.id, user.username or "", user.first_name or "")

    # Referral yoki kino deep link
    movie_code = None
    if args:
        arg = args[0]
        if arg.startswith("ref_"):
            ref_code = arg[4:]
            ref = db.get_ref(ref_code)
            if ref and is_new:
                result = db.add_ref_join(user.id, ref_code)
                # Limit to'lgan — adminga xabar
                if result == 'stopped':
                    s = db.get_ref_stats(ref_code)
                    try:
                        await context.bot.send_message(
                            cfg.OWNER_ID,
                            f"🔴 <b>Kampaniya to'xtatildi!</b>\n\n"
                            f"📢 <b>{ref['label']}</b>\n"
                            f"👥 Limit: <b>{ref['limit_count']}</b> ta\n"
                            f"✅ Jami keldi: <b>{s['total']}</b> ta\n\n"
                            f"<i>Kampaniyani davom ettirish uchun /ref → statistika → Davom ettirish</i>",
                            parse_mode="HTML"
                        )
                    except Exception:
                        pass
        else:
            movie_code = arg

    if db.is_banned(user.id):
        await update.message.reply_text(t("banned", _lang(user.id)))
        return

    # Yangi user — til tanlash
    if is_new:
        if movie_code:
            context.user_data["pending_code"] = movie_code
        await update.message.reply_text(
            t("choose_lang", "uz"),
            reply_markup=lang_keyboard(),
            parse_mode="HTML"
        )
        return

    lang = _lang(user.id)

    # Majburiy obuna
    not_subbed = await _check_sub(user.id, context.bot)
    if not_subbed:
        if movie_code:
            context.user_data["pending_code"] = movie_code
        await update.message.reply_text(
            t("sub_required", lang),
            reply_markup=subscription_keyboard(not_subbed, lang),
            parse_mode="HTML"
        )
        return

    # Kino deep link
    if movie_code:
        await _send_movie(update, context, movie_code, lang)
        return

    await update.message.reply_text(
        t("main_menu", lang),
        reply_markup=main_menu(lang),
        parse_mode="HTML"
    )


# ─── TIL TANLASH ─────────────────────────────────────────────────────────────

async def cb_lang(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    lang = query.data.split("_")[1]

    db.set_lang(user_id, lang)
    await query.message.edit_text(t("lang_set", lang), parse_mode="HTML")

    pending = context.user_data.pop("pending_code", None)
    if pending:
        not_subbed = await _check_sub(user_id, context.bot)
        if not_subbed:
            context.user_data["pending_code"] = pending
            await query.message.reply_text(
                t("sub_required", lang),
                reply_markup=subscription_keyboard(not_subbed, lang),
                parse_mode="HTML"
            )
            return
        await _send_movie_query(query, context, pending, lang)
        return

    await query.message.reply_text(
        t("main_menu", lang), reply_markup=main_menu(lang), parse_mode="HTML"
    )


# ─── OBUNA TEKSHIRISH ─────────────────────────────────────────────────────────

async def cb_check_sub(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    lang = _lang(user_id)

    not_subbed = await _check_sub(user_id, context.bot)
    if not_subbed:
        await query.message.edit_text(
            t("sub_not_done", lang),
            reply_markup=subscription_keyboard(not_subbed, lang),
            parse_mode="HTML"
        )
        return

    await query.message.edit_text(t("sub_ok", lang), parse_mode="HTML")

    pending = context.user_data.pop("pending_code", None)
    if pending:
        await _send_movie_query(query, context, pending, lang)
        return

    await context.bot.send_message(
        user_id, t("main_menu", lang), reply_markup=main_menu(lang), parse_mode="HTML"
    )


# ─── KINO YUBORISH ───────────────────────────────────────────────────────────

async def _send_movie(update, context, code, lang):
    user_id = update.effective_user.id
    movie = db.get_movie_by_code(code.strip())
    if not movie:
        await update.message.reply_text(t("movie_not_found", lang), parse_mode="HTML")
        return
    await _deliver_movie(context.bot, user_id, movie, lang)


async def _send_movie_query(query, context, code, lang):
    user_id = query.from_user.id
    movie = db.get_movie_by_code(code.strip())
    if not movie:
        await context.bot.send_message(user_id, t("movie_not_found", lang), parse_mode="HTML")
        return
    await _deliver_movie(context.bot, user_id, movie, lang)


async def _deliver_movie(bot, user_id, movie, lang):
    db.inc_views(movie["id"])
    db.add_history(user_id, movie["id"])
    is_fav  = db.is_favorite(user_id, movie["id"])
    protect = db.get_setting("save_block") == "1"

    cap = f"🎬 <b>{movie['title']}</b>\n━━━━━━━━━━━━━━━━━━━━\n"
    if movie.get("description"):
        cap += f"📝 {movie['description']}\n"
    if movie.get("year"):
        cap += f"📅 {'Yil' if lang == 'uz' else 'Год'}: {movie['year']}\n"
    if movie.get("genre"):
        cap += f"🎭 {'Janr' if lang == 'uz' else 'Жанр'}: {movie['genre']}\n"
    if movie.get("category"):
        cap += f"📂 {movie['category']}\n"
    cap += f"\n🆔 Kod: <code>{movie['code']}</code>"

    kb = movie_keyboard(movie["id"], is_fav, lang)
    try:
        await bot.send_video(
            user_id, video=movie["file_id"],
            caption=cap, parse_mode="HTML",
            reply_markup=kb, protect_content=protect
        )
    except Exception:
        await bot.send_document(
            user_id, document=movie["file_id"],
            caption=cap, parse_mode="HTML",
            reply_markup=kb, protect_content=protect
        )


# ─── XABAR HANDLER ───────────────────────────────────────────────────────────

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not db.get_user(user.id):
        await cmd_start(update, context)
        return
    if db.is_banned(user.id):
        return

    lang = _lang(user.id)
    not_subbed = await _check_sub(user.id, context.bot)
    if not_subbed:
        await update.message.reply_text(
            t("sub_required", lang),
            reply_markup=subscription_keyboard(not_subbed, lang),
            parse_mode="HTML"
        )
        return

    text = update.message.text.strip()

    if text in ("🎬 Kino qidirish", "🎬 Поиск фильма"):
        await update.message.reply_text(t("send_code", lang), parse_mode="HTML")
    elif text in ("⭐ Sevimlilar", "⭐ Избранное"):
        await _show_favorites(update, lang)
    elif text in ("🔥 TOP kinolar", "🔥 ТОП фильмов"):
        await _show_top(update, lang)
    elif text in ("🆕 Yangi kinolar", "🆕 Новые"):
        await _show_new(update, lang)
    elif text in ("📜 Tarix", "📜 История"):
        await _show_history(update, lang)
    elif text in ("🌐 Til", "🌐 Язык"):
        await update.message.reply_text(t("choose_lang", lang), reply_markup=lang_keyboard(), parse_mode="HTML")
    elif text in ("ℹ️ Yordam", "ℹ️ Помощь"):
        await update.message.reply_text(t("help", lang), parse_mode="HTML")
    else:
        await _send_movie(update, context, text, lang)


async def _show_favorites(update, lang):
    favs = db.get_favorites(update.effective_user.id)
    if not favs:
        await update.message.reply_text(t("favorites_empty", lang), parse_mode="HTML")
        return
    text = ("⭐ <b>Sevimli kinolar:</b>\n" if lang == "uz" else "⭐ <b>Избранные:</b>\n") + "━━━━━━━━━━━━━━━━━━━━\n"
    for f in favs:
        text += f"🎬 {f['title']} — <code>{f['code']}</code>\n"
    await update.message.reply_text(text, parse_mode="HTML")


async def _show_top(update, lang):
    top = db.get_top_movies()
    text = t("top_movies", lang) + "\n━━━━━━━━━━━━━━━━━━━━\n"
    for i, m in enumerate(top, 1):
        text += f"{i}. {m['title']} — <code>{m['code']}</code> 👁{m['views']}\n"
    await update.message.reply_text(text, parse_mode="HTML")


async def _show_new(update, lang):
    new = db.get_new_movies()
    text = t("new_movies", lang) + "\n━━━━━━━━━━━━━━━━━━━━\n"
    for m in new:
        text += f"🎬 {m['title']} — <code>{m['code']}</code>\n"
    await update.message.reply_text(text, parse_mode="HTML")


async def _show_history(update, lang):
    hist = db.get_history(update.effective_user.id)
    if not hist:
        await update.message.reply_text(t("history_empty", lang), parse_mode="HTML")
        return
    text = ("📜 <b>Oxirgi ko'rganlar:</b>\n" if lang == "uz" else "📜 <b>История:</b>\n") + "━━━━━━━━━━━━━━━━━━━━\n"
    for h in hist:
        text += f"🎬 {h['title']} — <code>{h['code']}</code>\n"
    await update.message.reply_text(text, parse_mode="HTML")


# ─── SEVIMLI CALLBACK ────────────────────────────────────────────────────────

async def cb_favorite(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id  = query.from_user.id
    lang     = _lang(user_id)
    parts    = query.data.split("_")
    action   = parts[1]
    movie_id = int(parts[2])

    if action == "add":
        db.add_favorite(user_id, movie_id)
        await query.answer(t("added_to_fav", lang), show_alert=True)
        kb = movie_keyboard(movie_id, True, lang)
    else:
        db.remove_favorite(user_id, movie_id)
        await query.answer(t("removed_from_fav", lang), show_alert=True)
        kb = movie_keyboard(movie_id, False, lang)

    try:
        await query.message.edit_reply_markup(reply_markup=kb)
    except Exception:
        pass
