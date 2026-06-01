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


# ─── /ref BUYRUG'I ───────────────────────────────────────────────────────────

async def cmd_ref(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Ruxsat yo'q!")
        return
    await update.message.reply_text(
        "🔗 <b>Referral tizimi</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "Har bir reklama beruvchi uchun alohida link yarating.\n"
        "Link orqali kelgan obunchilar avtomatik hisoblanadi.",
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
            "➕ <b>Yangi referral link</b>\n\n"
            "Kanal yoki reklama nomini yuboring:\n"
            "<i>Masalan: Kinolar UZ, Sarvar kanal, Reklama #1</i>",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 Orqaga", callback_data="ref_back")
            ]])
        )

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
            s = db.get_ref_stats(r["code"])
            kb.append([InlineKeyboardButton(
                f"📢 {r['label']} — 👥 {s['total']}",
                callback_data=f"ref_stats_{r['code']}"
            )])
        kb.append([InlineKeyboardButton("🔙 Orqaga", callback_data="ref_back")])
        await query.message.edit_text(
            "📋 <b>Barcha referral linklar:</b>",
            parse_mode="HTML", reply_markup=InlineKeyboardMarkup(kb)
        )

    elif data.startswith("ref_stats_"):
        code = data[len("ref_stats_"):]
        ref  = db.get_ref(code)
        if not ref:
            await query.message.edit_text("❌ Link topilmadi.")
            return
        s    = db.get_ref_stats(code)
        link = f"https://t.me/{cfg.BOT_USERNAME}?start=ref_{code}"

        daily_text = ""
        if s["daily"]:
            for d in s["daily"]:
                bar = "▓" * min(d["cnt"], 15)
                daily_text += f"\n{d['day'][5:]}  {bar} {d['cnt']}"
        else:
            daily_text = "\nMa'lumot yo'q"

        text = (
            f"📊 <b>{ref['label']}</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"👥 Jami kelganlar:  <b>{s['total']}</b>\n"
            f"📅 Bugun:           <b>{s['today']}</b>\n"
            f"📆 Oxirgi 7 kun:    <b>{s['week']}</b>\n\n"
            f"📈 <b>Kunlik grafik:</b>{daily_text}\n\n"
            f"🔗 <b>Reklama linki:</b>\n"
            f"<code>{link}</code>\n\n"
            f"<i>Shu linkni kanal egasiga yuboring</i>"
        )
        await query.message.edit_text(
            text, parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🗑 O'chirish", callback_data=f"ref_del_{code}")],
                [InlineKeyboardButton("🔙 Orqaga",    callback_data="ref_list")],
            ])
        )

    elif data.startswith("ref_del_"):
        code = data[len("ref_del_"):]
        db.delete_ref(code)
        await query.message.edit_text(
            "✅ Link o'chirildi!",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("📋 Ro'yxat", callback_data="ref_list")
            ]])
        )

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
            text += f"{i}. <b>{s['label']}</b> — 👥 <b>{s['total']}</b> kishi\n"
            total_all += s["total"]
        text += f"\n🔢 <b>Jami: {total_all} kishi</b>"
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
            "Har bir reklama beruvchi uchun alohida link yarating.",
            parse_mode="HTML", reply_markup=_ref_main_kb()
        )


# ─── STATE HANDLER ───────────────────────────────────────────────────────────

async def ref_state_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    state = context.user_data.get("ref_state")
    if not state:
        return False
    if not _is_admin(update.effective_user.id):
        return False

    text = update.message.text.strip() if update.message.text else ""

    if state == "waiting_label":
        code = _gen_code()
        ok   = db.create_ref(code, text, update.effective_user.id)
        context.user_data.pop("ref_state", None)

        if ok:
            link = f"https://t.me/{cfg.BOT_USERNAME}?start=ref_{code}"
            await update.message.reply_text(
                f"✅ <b>Link yaratildi!</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"📢 Nom: <b>{text}</b>\n"
                f"🔑 Kod: <code>{code}</code>\n\n"
                f"🔗 <b>Kanal egasiga beriladigan link:</b>\n"
                f"<code>{link}</code>\n\n"
                f"<i>Kim shu link orqali kelsa botda hisoblanadi.</i>",
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("📊 Statistika",   callback_data=f"ref_stats_{code}")],
                    [InlineKeyboardButton("📋 Barcha linklar", callback_data="ref_list")],
                ])
            )
        else:
            await update.message.reply_text("❌ Xatolik! Qaytadan urinib ko'ring.")
        return True

    return False
