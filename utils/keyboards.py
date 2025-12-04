from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def get_main_menu_keyboard():
    """
    Main menu keyboard (Lobby)
    """
    keyboard = [
        [InlineKeyboardButton("📨 ارسال نامه", callback_data="send_letter")],
        [InlineKeyboardButton("☕ کافه eynVu", callback_data="cafe_menu")],
        [
            InlineKeyboardButton("🏆 لیدربورد", callback_data="leaderboard"),
            InlineKeyboardButton("📋 لیست‌ها", callback_data="lists")
        ],
        [
            InlineKeyboardButton("🔗 سوشال مدیا", callback_data="social_media"),
            InlineKeyboardButton("👤 پروفایل من", callback_data="my_profile")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_send_letter_keyboard():
    """
    Send letter menu - choose recipient
    """
    keyboard = [
        [InlineKeyboardButton("📨 ارسال به عِین", callback_data="send_to_admin")],
        [InlineKeyboardButton("👥 ارسال به ادمین", callback_data="send_to_admins")],
        [InlineKeyboardButton("👤 ارسال به کاربر ناشناس", callback_data="send_to_user")],
        [InlineKeyboardButton("📋 قوانین پیام ناشناس", callback_data="rule_as")],
        [InlineKeyboardButton("🔙 برگشت به منوی اصلی", callback_data="back_to_main")]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_confirmation_keyboard():
    """
    Confirmation keyboard (Yes/No)
    """
    keyboard = [
        [
            InlineKeyboardButton("✅ آره", callback_data="confirm_yes"),
            InlineKeyboardButton("❌ نه", callback_data="confirm_no")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_message_actions_keyboard(sender_identifier: str):
    """
    Actions for received anonymous message (for admin/eyn)
    
    Args:
        sender_identifier: Identifier of message sender
    """
    keyboard = [
        [InlineKeyboardButton("👁️ مشاهده پیام", callback_data=f"view_msg_{sender_identifier}")],
        [
            InlineKeyboardButton("💬 پاسخ", callback_data=f"reply_{sender_identifier}"),
            InlineKeyboardButton("🗑️ حذف پیام", callback_data=f"delete_msg_{sender_identifier}")
        ],
        [
            InlineKeyboardButton("🚫 بلاک", callback_data=f"block_{sender_identifier}"),
            InlineKeyboardButton("👢 کیک", callback_data=f"kick_{sender_identifier}")
        ],
        [InlineKeyboardButton("⏱️ مسدود تایمی", callback_data=f"mute_{sender_identifier}")]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_cafe_menu_keyboard():
    """
    Cafe menu - choose table
    """
    keyboard = [
        [InlineKeyboardButton("📻 میز رادیو", callback_data="cafe_radio")],
        [InlineKeyboardButton("📚 میز کتابخانه", callback_data="cafe_library")],
        [InlineKeyboardButton("🎵 میز پلی‌لیست", callback_data="cafe_playlist")],
        [InlineKeyboardButton("🎙️ میز پادکست", callback_data="cafe_podcast")],
        [InlineKeyboardButton("🖼️ گوشه گالری", callback_data="cafe_gallery")],
        [InlineKeyboardButton("💻 طبقه بالا (کُد کافه)", callback_data="cafe_code")],
        [InlineKeyboardButton("🔙 برگشت به لابی", callback_data="back_to_main")]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_back_button(callback_data: str = "back_to_main"):
    """
    Simple back button
    """
    keyboard = [[InlineKeyboardButton("🔙 برگشت", callback_data=callback_data)]]
    return InlineKeyboardMarkup(keyboard)


def get_cancel_button():
    """
    Cancel button
    """
    keyboard = [[InlineKeyboardButton("❌ لغو", callback_data="cancel")]]
    return InlineKeyboardMarkup(keyboard)
