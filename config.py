import os

class Config:
    BOT_TOKEN    = os.getenv("BOT_TOKEN", "8621461817:AAHT3HBWe7ljJ64uDE13U1eDPVjmdiw1hVg")
    OWNER_ID     = int(os.getenv("OWNER_ID", "610489050"))
    DB_PATH      = os.getenv("DB_PATH", "kinobot.db")
    POST_CHANNEL = os.getenv("POST_CHANNEL", "-1004241881660")
    BOT_USERNAME = os.getenv("BOT_USERNAME", "YourBotUsername")  # ← BU NI O'ZGARTIRING!
