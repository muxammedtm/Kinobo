import random, string
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import Database
from config import Config

db  = Database()
cfg = Config()


def _is_admin(user_id):
    return user_id == cfg.OWNER_ID or user_id in db.get_admin_ids()

def _gen_code(length=8):
    chars = string.ascii_lowercase + string.digits
    return ''.join(random.choices(chars, k=length))

def _ref_main_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Yangi link yaratish", callback_data="ref_create")],
        [InlineKeyboardButton("Barcha linklar",      callback_data="ref_list")],
        [InlineKeyboardButton("Umumiy statistika",   callback_data="ref_allstats")],
    ])

def _status_icon(ref):
    if not ref["is_active"]:
        return "🔴"
    if ref["limit_count"] > 0:
        return "🟡"
    return "🟢"


# ─── /ref ────────────────────────────────────────────────────────────────────

async def cmd_ref(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _is_admin(update.effective_user.id):
        await update.message.reply_text("Ruxsat yoq!")
        return
    await update.message.reply_text(
        "🔗 <b>Referral tizimi</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "🟢 Faol  🟡 Limitli  🔴 Toxtatilgan\n\n"
        "Har bir kanal egasiga alohida link bering.\n"
        "Limit qoyilsa — belgilangan sondagi odam kelgach avtomatik toxtatadi.",
        parse_mode="HTML", reply_markup=_ref_main_kb()
    )


# ─── CALLBACKLAR ─────────────────────────────────────────────────────────────

async def ref_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    if not _is_admin(user_id):
        return

    data = query.data

    if data == "ref_create":
        context.user_data["ref_state"] = "waiting_label"
        await query.message.edit_text(
            "1-qadam: Kanal yoki reklama nomini yuboring:\n"
            "Masalan: Sarvar kanal, Reklama 1",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("Orqaga", callback_data="ref_back")
            ]])
        )

    elif data == "ref_list":
        refs = db.get_all_refs()
        if not refs:
            await query.message.edit_text(
                "Hozircha linklar yoq.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("Yaratish", callback_data="ref_create")],
                    [InlineKeyboardButton("Orqaga",   callback_data="ref_back")],
                ])
            )
            return
        kb = []
        for r in refs:
            s     = db.get_ref_stats(r["code"])
            icon  = _status_icon(r)
            total = s["total"]
            lim   = r["limit_count"]
            label = r["label"]
            code  = r["code"]
            lim_str = "/" + str(lim) if lim > 0 else ""
            btn_text = icon + " " + label + " — " + str(total) + lim_str
            kb.append([InlineKeyboardButton(btn_text, callback_data="ref_stats_" + code)])
        kb.append([InlineKeyboardButton("Orqaga", callback_data="ref_back")])
        await query.message.edit_text(
            "📋 <b>Barcha referral linklar:</b>",
            parse_mode="HTML", reply_markup=InlineKeyboardMarkup(kb)
        )

    elif data.startswith("ref_stats_"):
        code = data[len("ref_stats_"):]
        await _show_ref_stats(query, context, code)

    elif data.startswith("ref_setlimit_"):
        code = data[len("ref_setlimit_"):]
        context.user_data["ref_state"]      = "waiting_limit"
        context.user_data["ref_limit_code"] = code
        await query.message.edit_text(
            "🔢 <b>Limit oRnatish</b>\n\n"
            "Nechta odam kelgandan keyin toxtatsin?\n"
            "Limitisiz: 0 yuboring",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("Orqaga", callback_data="ref_stats_" + code)
            ]])
        )

    elif data.startswith("ref_stop_"):
        code = data[len("ref_stop_"):]
        db.stop_ref(code)
        await _show_ref_stats(query, context, code, msg="🔴 Kampaniya toxtatildi!")

    elif data.startswith("ref_resume_"):
        code = data[len("ref_resume_"):]
        db.resume_ref(code)
        await _show_ref_stats(query, context, code, msg="🟢 Kampaniya davom ettirildi!")

    elif data.startswith("ref_del_"):
        code = data[len("ref_del_"):]
        db.delete_ref(code)
        await query.message.edit_text(
            "Link ochirildi!",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("Royxat", callback_data="ref_list")
            ]])
        )

    elif data == "ref_allstats":
        all_s = db.get_all_ref_stats()
        if not all_s:
            await query.message.edit_text(
                "Hozircha statistika yoq.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("Orqaga", callback_data="ref_back")
                ]])
            )
            return
        text = "📊 <b>Umumiy referral statistika:</b>\n━━━━━━━━━━━━━━━━━━━━\n"
        total_all = 0
        for i, s in enumerate(all_s, 1):
            icon    = "🟢" if s["is_active"] else "🔴"
            lim     = s["limit_count"]
            lim_str = "/" + str(lim) if lim > 0 else ""
            label   = s["label"]
            total   = s["total"]
            text += str(i) + ". " + icon + " <b>" + label + "</b> — 👥 <b>" + str(total) + lim_str + "</b>\n"
            total_all += total
        text += "\n🔢 <b>Jami: " + str(total_all) + " kishi</b>"
        await query.message.edit_text(
            text, parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("Orqaga", callback_data="ref_back")
            ]])
        )

    elif data == "ref_back":
        await query.message.edit_text(
            "🔗 <b>Referral tizimi</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "🟢 Faol  🟡 Limitli  🔴 Toxtatilgan",
            parse_mode="HTML", reply_markup=_ref_main_kb()
        )


# ─── STATISTIKA ──────────────────────────────────────────────────────────────

async def _show_ref_stats(query, context, code, msg=""):
    ref = db.get_ref(code)
    if not ref:
        await query.message.edit_text("Link topilmadi.")
        return

    s    = db.get_ref_stats(code)
    link = "https://t.me/" + cfg.BOT_USERNAME + "?start=ref_" + code
    icon = _status_icon(ref)

    lim       = ref["limit_count"]
    total     = s["total"]
    is_active = ref["is_active"]
    label     = ref["label"]

    if lim > 0:
        lim_str = str(total) + "/" + str(lim)
    else:
        lim_str = str(total)

    if is_active and lim > 0:
        status = "🟡 Limitli (" + lim_str + ")"
    elif is_active:
        status = "🟢 Faol"
    else:
        status = "🔴 Toxtatilgan"

    lim_display = "Yoq (cheksiz)" if lim == 0 else str(lim)

    daily_text = ""
    if s["daily"]:
        for d in s["daily"]:
            bar = "▓" * min(d["cnt"], 15)
            day = d["day"][5:]
            cnt = d["cnt"]
            daily_text += "\n" + day + "  " + bar + " " + str(cnt)
    else:
        daily_text = "\nMalumot yoq"

    prefix = "\n\n" + msg + "\n" if msg else ""

    text = (
        prefix +
        "📊 <b>" + label + "</b> " + icon + "\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "Holat:       <b>" + status + "</b>\n"
        "Jami keldi:  <b>" + str(total) + "</b>\n"
        "Bugun:       <b>" + str(s["today"]) + "</b>\n"
        "7 kun:       <b>" + str(s["week"]) + "</b>\n"
        "Limit:       <b>" + lim_display + "</b>\n\n"
        "📈 <b>Kunlik grafik:</b>" + daily_text + "\n\n"
        "🔗 <b>Link:</b>\n<code>" + link + "</code>"
    )

    kb = []
    if is_active:
        kb.append([InlineKeyboardButton("🔢 Limit oRnatish", callback_data="ref_setlimit_" + code)])
        kb.append([InlineKeyboardButton("🔴 Toxtatish",      callback_data="ref_stop_" + code)])
    else:
        kb.append([InlineKeyboardButton("🟢 Davom ettirish", callback_data="ref_resume_" + code)])
    kb.append([InlineKeyboardButton("Ochirish",  callback_data="ref_del_" + code)])
    kb.append([InlineKeyboardButton("Orqaga",    callback_data="ref_list")])

    await query.message.edit_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(kb))


# ─── STATE HANDLER ───────────────────────────────────────────────────────────

async def ref_state_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    state = context.user_data.get("ref_state")
    if not state:
        return False
    if not _is_admin(update.effective_user.id):
        return False

    text = update.message.text.strip() if update.message.text else ""

    if state == "waiting_label":
        context.user_data["ref_label"] = text
        context.user_data["ref_state"] = "waiting_limit"
        context.user_data["ref_limit_code"] = None
        await update.message.reply_text(
            "2-qadam: Limit oRnating\n\n"
            "Nechta odam kelganda avtomatik toxtatsin?\n"
            "Limitsiz: 0 yuboring"
        )
        return True

    elif state == "waiting_limit":
        try:
            limit = int(text)
        except ValueError:
            await update.message.reply_text("Faqat raqam yuboring! Masalan: 100")
            return True

        existing_code = context.user_data.pop("ref_limit_code", None)
        context.user_data.pop("ref_state", None)

        if existing_code:
            db.set_ref_limit(existing_code, limit)
            if limit > 0:
                db.resume_ref(existing_code)
            s   = db.get_ref_stats(existing_code)
            ref = db.get_ref(existing_code)
            lim_text = str(limit) + " ta" if limit > 0 else "Yoq (cheksiz)"
            await update.message.reply_text(
                "Limit yangilandi!\n"
                "Nom: " + ref["label"] + "\n"
                "Yangi limit: " + lim_text + "\n"
                "Hozir: " + str(s["total"]) + " kishi",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("Statistika", callback_data="ref_stats_" + existing_code)
                ]])
            )
            return True

        label = context.user_data.pop("ref_label", "Nomsiz")
        code  = _gen_code()
        ok    = db.create_ref(code, label, update.effective_user.id, limit)

        if ok:
            link     = "https://t.me/" + cfg.BOT_USERNAME + "?start=ref_" + code
            lim_text = str(limit) + " ta odam" if limit > 0 else "Cheksiz"
            await update.message.reply_text(
                "✅ <b>Link yaratildi!</b>\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                "Nom:   <b>" + label + "</b>\n"
                "Limit: <b>" + lim_text + "</b>\n\n"
                "🔗 <b>Kanal egasiga beriladigan link:</b>\n"
                "<code>" + link + "</code>\n\n"
                "Kim shu link orqali kelsa hisoblanadi.\n"
                "Limit tolgan da bot avtomatik toxtatadi.",
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("Statistika",    callback_data="ref_stats_" + code)],
                    [InlineKeyboardButton("Barcha linklar", callback_data="ref_list")],
                ])
            )
        else:
            await update.message.reply_text("Xatolik! Qaytadan urinib koring.")
        return True

    return False
