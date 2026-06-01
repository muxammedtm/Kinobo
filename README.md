# 🎬 Mukammal Kino Bot — O'rnatish Qo'llanmasi

## 📁 Fayl Tuzilishi
```
kinobot/
├── main.py              ← Botni ishga tushirish
├── config.py            ← Token va sozlamalar
├── database.py          ← SQLite baza
├── keyboards.py         ← Barcha tugmalar
├── texts.py             ← O'zbek / Rus matnlar
├── requirements.txt
├── handlers/
│   ├── user.py          ← Foydalanuvchi funksiyalari
│   └── admin.py         ← Admin panel
└── README.md
```

---

## ⚙️ 1-QADAM: Sozlamalar — `config.py`

```python
BOT_TOKEN    = "1234567890:AAABB..."   # BotFather tokeni
OWNER_ID     = 123456789               # Sizning Telegram ID
POST_CHANNEL = "@kinolar_kanal"        # Kino post chiqadigan kanal (ixtiyoriy)
BOT_USERNAME = "MyKinoBot"             # Bot username (@ siz)
```

**Telegram ID qanday topish?**
→ [@userinfobot](https://t.me/userinfobot) ga `/start` yuboring

---

## 📦 2-QADAM: Kutubxona o'rnatish

```bash
pip install -r requirements.txt
```

---

## 🤖 3-QADAM: BotFather sozlamalari

1. [@BotFather](https://t.me/BotFather) → `/newbot`
2. Token oling → `config.py` ga qo'ying
3. `/setprivacy` → `Disable` (guruh uchun kerak bo'lsa)
4. `/setcommands` → quyidagini yuboring:
```
start - Botni boshlash
admin - Admin panel
```

---

## 🚀 4-QADAM: Botni ishga tushirish

```bash
python main.py
```

---

## 📢 Majburiy Kanal Sozlash

1. Botni kanalga **Admin** qiling (faqat "Members" huquqi kerak)
2. `/admin` → **📢 Kanallar** → **➕ Qo'shish**
3. Kanal username yuboring: `@kanalname`
4. **🔒 Obuna holati** → YOQISH

---

## 🎬 Kino Qo'shish

1. `/admin` → **🎬 Kinolar** → **➕ Qo'shish**
2. Nom → Tavsif (yoki /skip) → Yil → Janr → Kategoriya → **Kod** → **Fayl**
3. Agar `POST_CHANNEL` sozlangan bo'lsa, kanalga avtomatik post chiqadi

---

## 👑 Admin Rollari

| Rol | Tavsif |
|-----|--------|
| `super_admin` | Hamma narsaga ruxsat |
| `moderator` | Kinolar va userlarni boshqarish |
| `content_admin` | Faqat kino qo'shish/tahrirlash |
| `ads_admin` | Broadcast yuborish |

---

## 🔒 Himoya Tizimi

`/admin` → **⚙️ Sozlamalar:**
- ✅/❌ Forward bloklash
- ✅/❌ Saqlash bloklash (protect_content)

---

## 📨 Broadcast (Xabar Yuborish)

`/admin` → **📨 Broadcast:**
- **📨 Barchaga** — barcha foydalanuvchilarga
- **👥 Faollarga** — so'nggi 7 kun faol bo'lganlarga

Matn, rasm, video yoki dokument yuborsa bo'ladi.

---

## 🌐 bothost.ru da Deploy

1. Bothost.ru ga ro'yxatdan o'ting
2. Yangi Python loyiha yarating
3. Fayllarni yuklang
4. **Start file:** `main.py`
5. **Requirements:** `requirements.txt`
6. Environment Variables:
   ```
   BOT_TOKEN=sizning_tokeningiz
   OWNER_ID=sizning_id
   POST_CHANNEL=@kanalname
   BOT_USERNAME=botusername
   ```
7. Start tugmasini bosing ✅

---

## 🐛 Xato bo'lsa

`bot.log` faylini tekshiring:
```bash
tail -f bot.log
```
