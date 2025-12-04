from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes


async def rules_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /rules command - show all rule categories"""
    keyboard = [
        [InlineKeyboardButton("📨 قوانین پیام ناشناس", callback_data="rule_as")],
        [InlineKeyboardButton("📻 قوانین میز رادیو", callback_data="rule_ro")],
        [InlineKeyboardButton("📚 قوانین کتابخانه", callback_data="rule_lb")],
        [InlineKeyboardButton("🎵 قوانین پلی‌لیست", callback_data="rule_pl")],
        [InlineKeyboardButton("🖼️ قوانین گالری", callback_data="rule_ga")],
        [InlineKeyboardButton("💻 قوانین کُد کافه", callback_data="rule_cc")],
        [InlineKeyboardButton("🔙 بستن", callback_data="close_rules")]
    ]
    
    text = """
📋 قوانین و مقررات eynVu

لطفاً قبل از استفاده از هر بخش، قوانین مربوط به آن را مطالعه کنید:
"""
    
    await update.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def show_rule_as(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show anonymous messaging rules"""
    query = update.callback_query
    await query.answer()
    
    text = """
📨 قوانین پیام ناشناس (Anonymous Messaging)

━━━━━━━━━━━━━━━━━━━━

⚠️ نکات مهم:

🔹 پیام‌های شما به صورت کاملاً ناشناس ارسال می‌شود

🔹 در نامه‌ها به دیگران توهین نکنید
   › هرگونه مشاهده و گزارش این‌گونه پیام‌ها منجر به بن دائمی شما خواهد شد

🔹 ارسال تصاویر، ویدیو و محتوای نامناسب ممنوع
   › ارسال محتوایی با هدف آزار و اذیت دیگران مشاهده و بررسی می‌شود

🔹 از ارسال مکرر و اسپم خودداری کنید
   › ارسال بیش از حد پیام به یک نفر = بن موقت

━━━━━━━━━━━━━━━━━━━━

💬 گزارش مشکلات:

مشکلات و پیشنهادات خود را با باز کردن تیکت با ما در میان بگذارید.

⚠️ لطفاً مشکلات را از طریق پیام ناشناس ارسال نکنید.

━━━━━━━━━━━━━━━━━━━━

با رعایت این قوانین، به ایجاد فضایی دوستانه و امن کمک کنید 💚
"""
    
    keyboard = [[InlineKeyboardButton("🔙 برگشت به قوانین", callback_data="back_to_rules")]]
    
    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def back_to_rules(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Go back to rules menu"""
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("📨 قوانین پیام ناشناس", callback_data="rule_as")],
        [InlineKeyboardButton("📻 قوانین میز رادیو", callback_data="rule_ro")],
        [InlineKeyboardButton("📚 قوانین کتابخانه", callback_data="rule_lb")],
        [InlineKeyboardButton("🎵 قوانین پلی‌لیست", callback_data="rule_pl")],
        [InlineKeyboardButton("🖼️ قوانین گالری", callback_data="rule_ga")],
        [InlineKeyboardButton("💻 قوانین کُد کافه", callback_data="rule_cc")],
        [InlineKeyboardButton("🔙 بستن", callback_data="close_rules")]
    ]
    
    text = """
📋 قوانین و مقررات eynVu

لطفاً قبل از استفاده از هر بخش، قوانین مربوط به آن را مطالعه کنید:
"""
    
    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def close_rules(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Close rules menu"""
    query = update.callback_query
    await query.answer()
    await query.message.delete()
