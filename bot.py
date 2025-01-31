import sqlite3
import os
import asyncio
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, CallbackContext
from dotenv import load_dotenv
from flask import Flask  # Required for Render

# Load environment variables
load_dotenv()

# Initialize Flask app for Render compatibility
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

# Database setup (unchanged)
def init_db():
    conn = sqlite3.connect('books.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS books
                 (id INTEGER PRIMARY KEY, book_title TEXT UNIQUE)''')
    conn.commit()
    conn.close()

# Add a book to the database (unchanged)
def add_book(book_title):
    conn = sqlite3.connect('books.db')
    c = conn.cursor()
    try:
        c.execute("INSERT INTO books (book_title) VALUES (?)", (book_title,))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

# Check if a book exists (unchanged)
def check_book(book_title):
    conn = sqlite3.connect('books.db')
    c = conn.cursor()
    c.execute("SELECT * FROM books WHERE book_title=?", (book_title,))
    result = c.fetchone()
    conn.close()
    return result is not None

# Telegram bot handler (unchanged)
async def handle_message(update: Update, context: CallbackContext):
    book_title = update.message.text
    if check_book(book_title):
        await update.message.reply_text(f"⚠️ This book already exists: {book_title}")
    else:
        add_book(book_title)
        await update.message.reply_text(f"✅ New book added: {book_title}")

async def run_bot():
    application = Application.builder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    await application.run_polling()

def main():
    init_db()
    # Start Flask server in a separate thread (required for Render)
    from threading import Thread
    Thread(target=lambda: app.run(host='0.0.0.0', port=8080, debug=False, use_reloader=False)).start()
    # Start the Telegram bot
    asyncio.run(run_bot())

if __name__ == "__main__":
    # Remove Windows-specific code entirely for Render
    main()
