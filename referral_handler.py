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
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def _ref_main_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Yangi link yaratish", callback_data="ref_create")],
        [InlineKeyboardButton("📋 Barcha linklar",      callback_data="ref_list")],
        [InlineKeyboardButton("📊 Umumiy statistika",   callback_data="ref_allstats")],
    ])

def _status_icon(ref):
    if not ref['is_active']:
        return "🔴"
    if ref['limit_count'] > 0:
        return "🟡"
    return "🟢"


# ─── /ref ────────────────────────────────────────────────────────────────────

async def cmd_ref(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Ruxsat yo'q!")
        return
    await update.message.reply_text(
        "🔗 <b>Referral tizimi</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "🟢 Faol  🟡 Limitli  🔴 To'xtatilgan\n\n"
        "Har bir kanal egasiga alohida link bering.\n"
        "Limit qo'yilsa — belgilangan sondagi odam kelgach avtomatik to'xtaydi.",
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

    # ── Yangi link ────────────────────────────────────────────────────────────
    if data == "ref_create":
        context.user_data["ref_state"] = "waiting_label"
        await query.message.edit_text(
            "➕ <b>1-qadam:</b> Kanal yoki reklama nomini yuboring:\n"
            "<i>Masalan: Sarvar kanal, Reklama #1</i>",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 Orqaga", callback_data="ref_back")
            ]])
        )

    # ── Ro'yxat ───────────────────────────────────────────────────────────────
    elif data == "ref_list":
        refs = db.get_all_refs()
        if not refs:
            await query.message.edit_text(
                "📋 Hozircha linklar yo'q.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("➕ Yaratish", callback_data="ref_create")],
                    [InlineKeyboardButton("🔙 Orqaga",   callback_data="ref_back")],
                ])
            )
            return
        kb = []
        for r in refs:
            s    = db.get_ref_stats(r["code"])
            icon = _status_icon(r)
            lim  = f"/{r['limit_count']}" if r['limit_count'] > 0 else ""
            kb.append([InlineKeyboardButton(
                f"{icon} {r['label']} — 👥{s['total']}{lim}",
                callback_data=f"ref_stats_{r['code']}"
            )])
        kb.append([InlineKeyboardButton("🔙 Orqaga", callback_data="ref_back")])
        await query.message.edit_text(
            "📋 <b>Barcha referral linklar:</b>",
            parse_mode="HTML", reply_markup=InlineKeyboardMarkup(kb)
        )

    # ── Statistika ────────────────────────────────────────────────────────────
    elif data.startswith("ref_stats_"):
        code = data[len("ref_stats_"):]
        await _show_ref_stats(query, code)

    # ── Limit o'rnatish ───────────────────────────────────────────────────────
    elif data.startswith("ref_setlimit_"):
        code = data[len("ref_setlimit_"):]
        context.user_data["ref_state"]      = "waiting_limit"
        context.user_data["ref_limit_code"] = code
        await query.message.edit_text(
            "🔢 <b>Limit o'rnatish</b>\n\n"
            "Nechta odam kelgandan keyin to'xtatsin?\n"
            "<i>Masalan: 100, 500, 1000</i>\n\n"
            "Limitni o'chirish uchun: <code>0</code> yuboring",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 Orqaga", callback_data=f"ref_stats_{code}")
            ]])
        )

    # ── To'xtatish / Davom ettirish ───────────────────────────────────────────
    elif data.startswith("ref_stop_"):
        code = data[len("ref_stop_"):]
        db.stop_ref(code)
        await _show_ref_stats(query, code, msg="🔴 Kampaniya to'xtatildi!")

    elif data.startswith("ref_resume_"):
        code = data[len("ref_resume_"):]
        db.resume_ref(code)
        await _show_ref_stats(query, code, msg="🟢 Kampaniya davom ettirildi!")

    # ── O'chirish ─────────────────────────────────────────────────────────────
    elif data.startswith("ref_del_"):
        code = data[len("ref_del_"):]
        db.delete_ref(code)
        await query.message.edit_text(
            "✅ Link o'chirildi!",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("📋 Ro'yxat", callback_data="ref_list")
            ]])
        )

    # ── Umumiy statistika ─────────────────────────────────────────────────────
    elif data == "ref_allstats":
        all_s = db.get_all_ref_stats()
        if not all_s:
            await query.message.edit_text(
                "📊 Hozircha statistika yo'q.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 Orqaga", callback_data="ref_back")
                ]])
            )
            return
        text = "📊 <b>Umumiy referral statistika:</b>\n━━━━━━━━━━━━━━━━━━━━\n"
        total_all = 0
        for i, s in enumerate(all_s, 1):
            icon = "🟢" if s['is_active'] else "🔴"
            lim  = f"/{s['limit_count']}" if s['limit_count'] > 0 else ""
            text += f"{i}. {icon} <b>{s['label']}</b> — 👥 <b>{s['total']}{lim}</b>\n"
            total_all += s["total"]
        text += f"\n🔢 <b>Jami barcha linklardan: {total_all} kishi</b>"
        await query.message.edit_text(
            text, parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 Orqaga", callback_data="ref_back")
            ]])
        )

    elif data == "ref_back":
        await query.message.edit_text(
            "🔗 <b>Referral tizimi</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "🟢 Faol  🟡 Limitli  🔴 To'xtatilgan",
            parse_mode="HTML", reply_markup=_ref_main_kb()
        )


# ─── STATISTIKA CHIQARISH ────────────────────────────────────────────────────

async def _show_ref_stats(query, code, msg=""):
    ref = db.get_ref(code)
    if not ref:
        await query.message.edit_text("❌ Link topilmadi.")
        return
    s    = db.get_ref_stats(code)
    link = f"https://t.me/{cfg.BOT_USERNAME}?start=ref_{code}"
    icon = _status_icon(ref)

    lim_text = f"{s['total']}/{ref['limit_count']}" if ref['limit_count'] > 0 else str(s['total'])
    status   = "🟢 Faol" if ref['is_active'] else "🔴 To'xtatilgan"
    if ref['is_active'] and ref['limit_count'] > 0:
        status = f"🟡 Limitli ({lim_text})"

    daily_text = ""
    if s["daily"]:
        for d in s["daily"]:
            bar = "▓" * min(d["cnt"], 15)
            daily_text += f"\n{d['day'][5:]}  {bar} {d['cnt']}"
    else:
        daily_text = "\nMa'lumot yo'q"

    top = f"\n\n{msg}" if msg else ""

    text = (
        f"{top}"
        f"📊 <b>{ref['label']}</b> {icon}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"⚡ Holat:         <b>{status}</b>\n"
        f"👥 Jami keldi:   <b>{s['total']}</b>\n"
        f"📅 Bugun:        <b>{s['today']}</b>\n"
        f"📆 7 kun:        <b>{s['week']}</b>\n"
        f"🔢 Limit:        <b>{'Yo\'q' if ref['limit_count']==0 else ref['limit_count']}</b>\n\n"
        f"📈 <b>Kunlik grafik:</b>{daily_text}\n\n"
        f"🔗 <b>Link:</b>\n<code>{link}</code>"
    )

    # Tugmalar
    kb = []
    if ref['is_active']:
        kb.append([InlineKeyboardButton("🔢 Limit o'rnatish", callback_data=f"ref_setlimit_{code}")])
        kb.append([InlineKeyboardButton("🔴 To'xtatish",      callback_data=f"ref_stop_{code}")])
    else:
        kb.append([InlineKeyboardButton("🟢 Davom ettirish",  callback_data=f"ref_resume_{code}")])
    kb.append([InlineKeyboardButton("🗑 O'chirish",           callback_data=f"ref_del_{code}")])
    kb.append([InlineKeyboardButton("🔙 Orqaga",              callback_data="ref_list")])

    await query.message.edit_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(kb))


# ─── STATE HANDLER ───────────────────────────────────────────────────────────

async def ref_state_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    state = context.user_data.get("ref_state")
    if not state:
        return False
    if not _is_admin(update.effective_user.id):
        return False

    text = update.message.text.strip() if update.message.text else ""

    # ── 1-qadam: nom ─────────────────────────────────────────────────────────
    if state == "waiting_label":
        context.user_data["ref_label"] = text
        context.user_data["ref_state"] = "waiting_limit"
        context.user_data["ref_limit_code"] = None  # yangi
        await update.message.reply_text(
            "🔢 <b>2-qadam:</b> Limit o'rnating\n\n"
            "Nechta odam kelganda avtomatik to'xtatsin?\n"
            "<i>Limitisiz qoldirish uchun: <code>0</code> yuboring</i>",
            parse_mode="HTML"
        )
        return True

    # ── 2-qadam: limit ───────────────────────────────────────────────────────
    elif state == "waiting_limit":
        try:
            limit = int(text)
        except ValueError:
            await update.message.reply_text("❌ Faqat raqam yuboring! Masalan: <code>100</code>", parse_mode="HTML")
            return True

        existing_code = context.user_data.pop("ref_limit_code", None)
        context.user_data.pop("ref_state", None)

        # Mavjud link uchun limit yangilash
        if existing_code:
            db.set_ref_limit(existing_code, limit)
            if limit > 0:
                db.resume_ref(existing_code)
            s    = db.get_ref_stats(existing_code)
            ref  = db.get_ref(existing_code)
            lim_text = f"{limit} ta" if limit > 0 else "Yo'q (cheksiz)"
            await update.message.reply_text(
                f"✅ <b>Limit yangilandi!</b>\n"
                f"📢 {ref['label']}\n"
                f"🔢 Yangi limit: <b>{lim_text}</b>\n"
                f"👥 Hozir: <b>{s['total']}</b> kishi",
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("📊 Statistika", callback_data=f"ref_stats_{existing_code}")
                ]])
            )
            return True

        # Yangi link yaratish
        label = context.user_data.pop("ref_label", "Nomsiz")
        code  = _gen_code()
        ok    = db.create_ref(code, label, update.effective_user.id, limit)

        if ok:
            link     = f"https://t.me/{cfg.BOT_USERNAME}?start=ref_{code}"
            lim_text = f"{limit} ta odam" if limit > 0 else "Cheksiz"
            await update.message.reply_text(
                f"✅ <b>Link yaratildi!</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"📢 Nom:   <b>{label}</b>\n"
                f"🔢 Limit: <b>{lim_text}</b>\n\n"
                f"🔗 <b>Kanal egasiga beriladigan link:</b>\n"
                f"<code>{link}</code>\n\n"
                f"<i>Kim shu link orqali kelsa hisoblanadi.\n"
                f"Limit to'lganda bot avtomatik to'xtatadi va sizga xabar beradi.</i>",
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("📊 Statistika",    callback_data=f"ref_stats_{code}")],
                    [InlineKeyboardButton("📋 Barcha linklar", callback_data="ref_list")],
                ])
            )
        else:
            await update.message.reply_text("❌ Xatolik! Qaytadan urinib ko'ring.")
        return True

    return False
