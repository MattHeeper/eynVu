from telegram import Update
from telegram.ext import ContextTypes

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Simple test"""
    try:
        await update.message.reply_text("سلام! ربات کار میکنه ✅")
        print(f"✅ /start from user: {update.effective_user.id}")
    except Exception as e:
        print(f"❌ Error: {e}")
