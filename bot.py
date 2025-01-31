import sqlite3
import os
import asyncio
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, CallbackContext
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database setup
def init_db():
    conn = sqlite3.connect('books.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS books
                 (id INTEGER PRIMARY KEY, book_title TEXT UNIQUE)''')
    conn.commit()
    conn.close()

# Add a book to the database
def add_book(book_title):
    conn = sqlite3.connect('books.db')
    c = conn.cursor()
    try:
        c.execute("INSERT INTO books (book_title) VALUES (?)", (book_title,))
        conn.commit()
        return True
    except sqlite3.IntegrityError:  # Duplicate entry
        return False
    finally:
        conn.close()

# Check if a book exists
def check_book(book_title):
    conn = sqlite3.connect('books.db')
    c = conn.cursor()
    c.execute("SELECT * FROM books WHERE book_title=?", (book_title,))
    result = c.fetchone()
    conn.close()
    return result is not None

# Telegram bot handlers
async def handle_message(update: Update, context: CallbackContext):
    book_title = update.message.text
    if check_book(book_title):
        await update.message.reply_text(f"⚠️ This book already exists: {book_title}")
    else:
        add_book(book_title)
        await update.message.reply_text(f"✅ New book added: {book_title}")

def main():
    init_db()
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

    if not TELEGRAM_BOT_TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN environment variable not set.")

    # Set Windows event loop policy (required for Windows + Python 3.8+)
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    # Build the application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start the bot
    print("Bot is running...")
    application.run_polling()

if __name__ == "__main__":
    main()
