TEXTS = {
    # ─── TIL TANLASH ──────────────────────────────
    "choose_lang": {
        "uz": "🌐 Tilni tanlang:\n<i>Выберите язык:</i>",
        "ru": "🌐 Выберите язык:\n<i>Tilni tanlang:</i>",
    },
    "lang_set": {
        "uz": "✅ Til o'rnatildi: O'zbek 🇺🇿",
        "ru": "✅ Язык установлен: Русский 🇷🇺",
    },

    # ─── ASOSIY MENYU ─────────────────────────────
    "main_menu": {
        "uz": (
            "🎬 <b>Kino Bot</b> ga xush kelibsiz!\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "📌 Kino kodini yuboring yoki quyidagi bo'limlardan foydalaning:"
        ),
        "ru": (
            "🎬 Добро пожаловать в <b>Kino Bot</b>!\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "📌 Отправьте код фильма или воспользуйтесь разделами ниже:"
        ),
    },

    # ─── OBUNA ────────────────────────────────────
    "sub_required": {
        "uz": (
            "🔒 <b>Botdan foydalanish uchun quyidagi kanallarga obuna bo'ling:</b>\n\n"
            "Obuna bo'lgach ✅ <b>Tekshirish</b> tugmasini bosing."
        ),
        "ru": (
            "🔒 <b>Для использования бота подпишитесь на каналы ниже:</b>\n\n"
            "После подписки нажмите ✅ <b>Проверить</b>."
        ),
    },
    "sub_not_done": {
        "uz": "❌ Hali barcha kanallarga obuna bo'lmadingiz!\n\nQuyidagilarga obuna bo'ling:",
        "ru": "❌ Вы ещё не подписались на все каналы!\n\nПодпишитесь на следующие:",
    },
    "sub_ok": {
        "uz": "✅ <b>Obuna tasdiqlandi!</b> Botdan foydalanishingiz mumkin.",
        "ru": "✅ <b>Подписка подтверждена!</b> Вы можете пользоваться ботом.",
    },

    # ─── KINO ─────────────────────────────────────
    "movie_not_found": {
        "uz": "❌ <b>Kino topilmadi.</b>\n\nTo'g'ri kodni yuboring yoki /help buyrug'ini ko'ring.",
        "ru": "❌ <b>Фильм не найден.</b>\n\nОтправьте правильный код или смотрите /help.",
    },
    "send_code": {
        "uz": "🔢 Kino kodini yuboring:",
        "ru": "🔢 Отправьте код фильма:",
    },

    # ─── SEVIMLILAR ───────────────────────────────
    "favorites_empty": {
        "uz": "⭐ Hozircha sevimli kinolar yo'q.\n\nKino topib ⭐ tugmasini bosing.",
        "ru": "⭐ Избранных фильмов пока нет.\n\nНайдите фильм и нажмите ⭐.",
    },
    "added_to_fav": {
        "uz": "⭐ Sevimlilarga qo'shildi!",
        "ru": "⭐ Добавлено в избранное!",
    },
    "removed_from_fav": {
        "uz": "🗑 Sevimlilardan o'chirildi.",
        "ru": "🗑 Удалено из избранного.",
    },

    # ─── TARIX ────────────────────────────────────
    "history_empty": {
        "uz": "📜 Qidiruvlar tarixi bo'sh.",
        "ru": "📜 История поиска пуста.",
    },

    # ─── TOP / YANGI ──────────────────────────────
    "top_movies": {
        "uz": "🔥 <b>TOP 10 Kinolar</b> (Ko'rilganlar soni bo'yicha):",
        "ru": "🔥 <b>ТОП 10 фильмов</b> (по количеству просмотров):",
    },
    "new_movies": {
        "uz": "🆕 <b>Yangi qo'shilgan kinolar:</b>",
        "ru": "🆕 <b>Новые фильмы:</b>",
    },

    # ─── YORDAM ───────────────────────────────────
    "help": {
        "uz": (
            "ℹ️ <b>Yordam</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "🎬 Kino olish uchun uning <b>kodini</b> yuboring.\n"
            "Kod odatda 3-6 ta raqamdan iborat.\n\n"
            "<b>Bo'limlar:</b>\n"
            "🎬 Kino qidirish — kod yuborish\n"
            "⭐ Sevimlilar — saqlangan kinolar\n"
            "🔥 TOP — eng ko'p ko'rilganlar\n"
            "🆕 Yangi — yangi qo'shilganlar\n"
            "📜 Tarix — oxirgi ko'rganlaringiz\n"
            "🌐 Til — tilni o'zgartirish"
        ),
        "ru": (
            "ℹ️ <b>Помощь</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "🎬 Чтобы получить фильм, отправьте его <b>код</b>.\n"
            "Код обычно состоит из 3-6 цифр.\n\n"
            "<b>Разделы:</b>\n"
            "🎬 Поиск фильма — отправить код\n"
            "⭐ Избранное — сохранённые фильмы\n"
            "🔥 ТОП — самые просматриваемые\n"
            "🆕 Новые — последние добавления\n"
            "📜 История — ваши последние просмотры\n"
            "🌐 Язык — сменить язык"
        ),
    },

    # ─── BAN ──────────────────────────────────────
    "banned": {
        "uz": "🚫 Siz botdan bloklangansiz.",
        "ru": "🚫 Вы заблокированы в боте.",
    },
}

def t(key: str, lang: str = "uz") -> str:
    entry = TEXTS.get(key, {})
    return entry.get(lang, entry.get("uz", key))
