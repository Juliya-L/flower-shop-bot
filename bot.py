from dotenv import load_dotenv
import os
from telegram.ext import ApplicationBuilder
from handlers import register_handlers

load_dotenv()

TOKEN = os.getenv("TOKEN")
if not TOKEN or TOKEN == "your_bot_token_here":
    raise ValueError("Please set TOKEN in .env file (see .env.example)")

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    register_handlers(app)
    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
