import os

class Config:
    BOT_TOKEN    = os.getenv("BOT_TOKEN", "8621461817:AAHT3HBWe7ljJ64uDE13U1eDPVjmdiw1hVg")
    OWNER_ID     = int(os.getenv("OWNER_ID", "610489050"))
    DB_PATH      = os.getenv("DB_PATH", "kinobot.db")
    POST_CHANNEL = os.getenv("POST_CHANNEL", "")  # Admin paneldan o'rnatiladi
    BOT_USERNAME = os.getenv("BOT_USERNAME", "FilmLaringiz")  # ← BU NI O'ZGARTIRING!
