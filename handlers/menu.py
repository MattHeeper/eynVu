from telegram import Update
from telegram.ext import ContextTypes
from utils.keyboards import (
    get_main_menu_keyboard,
    get_send_letter_keyboard,
    get_cafe_menu_keyboard
)
from utils.messages import (
    get_main_menu_text,
    get_send_letter_text,
    get_cafe_menu_text
)


async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle /menu command
    Show main menu
    """
    await update.message.reply_text(
        get_main_menu_text(),
        reply_markup=get_main_menu_keyboard()
    )


async def handle_main_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle callback queries for main menu
    """
    query = update.callback_query
    await query.answer()
    
    callback_data = query.data
    
    # Back to main menu
    if callback_data == "back_to_main":
        await query.edit_message_text(
            get_main_menu_text(),
            reply_markup=get_main_menu_keyboard()
        )
    
    # Send letter menu
    elif callback_data == "send_letter":
        await query.edit_message_text(
            get_send_letter_text(),
            reply_markup=get_send_letter_keyboard()
        )
    
    # Cafe menu
    elif callback_data == "cafe_menu":
        await query.edit_message_text(
            get_cafe_menu_text(),
            reply_markup=get_cafe_menu_keyboard()
        )
    
    # Leaderboard (placeholder)
    elif callback_data == "leaderboard":
        await query.edit_message_text(
            "🏆 لیدربورد\n\n🚧 این بخش در حال توسعه است...",
            reply_markup=get_main_menu_keyboard()
        )
    
    # Lists (placeholder)
    elif callback_data == "lists":
        await query.edit_message_text(
            "📋 لیست‌ها\n\n🚧 این بخش در حال توسعه است...",
            reply_markup=get_main_menu_keyboard()
        )
    
    # Social media (placeholder)
    elif callback_data == "social_media":
        await query.edit_message_text(
            "🔗 سوشال مدیا\n\n🚧 این بخش در حال توسعه است...",
            reply_markup=get_main_menu_keyboard()
        )
    
    # My profile (placeholder)
    elif callback_data == "my_profile":
        await query.edit_message_text(
            "👤 پروفایل من\n\n🚧 این بخش در حال توسعه است...",
            reply_markup=get_main_menu_keyboard()
        )
