import sqlite3
import os
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, filters, CallbackContext  # Use 'filters' instead of 'Filters'
from dotenv import load_dotenv  # For loading environment variables from .env file

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
def handle_message(update: Update, context: CallbackContext):
    book_title = update.message.text  # Assume the book title is sent as a message
    if check_book(book_title):
        update.message.reply_text(f"⚠️ This book already exists in the channel: {book_title}")
    else:
        add_book(book_title)
        update.message.reply_text(f"✅ New book added: {book_title}")

def main():
    init_db()
    # Get the API token from environment variables
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    if not TELEGRAM_BOT_TOKEN:
        raise ValueError("Please set the TELEGRAM_BOT_TOKEN environment variable.")

    updater = Updater(TELEGRAM_BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))  # Use 'filters.TEXT' and 'filters.COMMAND'

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
