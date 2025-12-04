from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import Session
from models.user import User
from models.message import AnonymousMessage
from models.log import Log
from models.identifier import generate_identifier
from utils.state import set_state, get_state, clear_state, STATE_WAITING_MESSAGE, STATE_WAITING_CONFIRMATION
from config import Config


async def start_send_to_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start sending to main admin (you)"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    set_state(user_id, STATE_WAITING_MESSAGE, {
        "recipient": "admin",
        "recipient_id": Config.ADMIN_ID
    })
    
    await query.edit_message_text(
        "📨 ارسال نامه به عِین\n\n"
        "پیام خود را بفرستید:",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("❌ لغو", callback_data="cancel_send")
        ]])
    )


async def start_send_to_admins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show list of admins to send to"""
    query = update.callback_query
    await query.answer()
    
    db = Session()
    try:
        # Get all admin users
        admin_users = db.query(User).filter(
            User.telegram_id.in_(Config.ADMIN_IDS)
        ).all()
        
        if not admin_users:
            await query.edit_message_text(
                "❌ هیچ ادمینی یافت نشد",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 برگشت", callback_data="send_letter")
                ]])
            )
            return
        
        # Create keyboard with admin list
        keyboard = []
        for admin in admin_users:
            name = admin.nickname or admin.first_name
            keyboard.append([
                InlineKeyboardButton(
                    f"👤 {name}",
                    callback_data=f"send_to_specific_{admin.telegram_id}"
                )
            ])
        keyboard.append([InlineKeyboardButton("🔙 برگشت", callback_data="send_letter")])
        
        await query.edit_message_text(
            "👥 انتخاب ادمین:\n\nبه کدوم ادمین پیام بفرستی؟",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    finally:
        db.close()


async def start_send_to_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Request user identifier to send anonymous message"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    set_state(user_id, "WAITING_IDENTIFIER", {})
    
    await query.edit_message_text(
        "👤 ارسال به کاربر ناشناس\n\n"
        "شناسه اختصاصی کاربر را وارد کن:\n"
        "(مثال: Ua1@gb2h)",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("❌ لغو", callback_data="cancel_send")
        ]])
    )


async def handle_identifier_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle user identifier input"""
    user_id = update.effective_user.id
    state = get_state(user_id)
    
    if state["state"] != "WAITING_IDENTIFIER":
        return
    
    identifier = update.message.text.strip()
    db = Session()
    
    try:
        # Find user by identifier
        target_user = db.query(User).filter(User.identifier == identifier).first()
        
        if not target_user:
            from difflib import get_close_matches
            all_identifiers = [u.identifier for u in db.query(User.identifier).all()]
            suggestions = get_close_matches(identifier, all_identifiers, n=3, cutoff=0.6)
            
            suggestion_text = ""
            if suggestions:
                suggestion_text = "\n\n🔍 شاید منظورت یکی از این‌ها بود:\n"
                for sugg in suggestions:
                    suggestion_text += f"  › `{sugg}`\n"
            
            await update.message.reply_text(
                f"❌ کاربر با شناسه `{identifier}` یافت نشد{suggestion_text}\n\nدوباره تلاش کن:",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("❌ لغو", callback_data="cancel_send")
                ]])
            )
            return
        
        # Set state for message input
        set_state(user_id, STATE_WAITING_MESSAGE, {
            "recipient": "user",
            "recipient_id": target_user.telegram_id,
            "recipient_identifier": identifier
        })
        
        await update.message.reply_text(
            f"✅ کاربر یافت شد: {identifier}\n\nپیام خود را بفرستید:",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("❌ لغو", callback_data="cancel_send")
            ]])
        )
    finally:
        db.close()

async def start_send_to_specific(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start sending to specific admin"""
    query = update.callback_query
    await query.answer()
    
    # Extract telegram_id from callback_data
    recipient_id = int(query.data.split("_")[-1])
    
    user_id = update.effective_user.id
    set_state(user_id, STATE_WAITING_MESSAGE, {
        "recipient": "admin",
        "recipient_id": recipient_id
    })
    
    await query.edit_message_text(
        "📨 ارسال نامه به ادمین\n\nپیام خود را بفرستید:",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("❌ لغو", callback_data="cancel_send")
        ]])
    )


async def handle_message_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming message"""
    user_id = update.effective_user.id
    state = get_state(user_id)
    
    if state["state"] == "WAITING_IDENTIFIER":
        await handle_identifier_input(update, context)
        return
    
    if state["state"] != STATE_WAITING_MESSAGE:
        return
    
    message = update.message
    message_text = message.text or message.caption
    message_type = "text"
    file_id = None
    
    if message.photo:
        message_type = "photo"
        file_id = message.photo[-1].file_id
    elif message.voice:
        message_type = "voice"
        file_id = message.voice.file_id
    
    preview = message_text[:100] if message_text else f"[{message_type}]"
    if message_text and len(message_text) > 100:
        preview += "..."
    
    set_state(user_id, STATE_WAITING_CONFIRMATION, {
        **state["data"],
        "message_text": message_text,
        "message_type": message_type,
        "file_id": file_id
    })
    
    keyboard = [
        [
            InlineKeyboardButton("✅ آره", callback_data="confirm_send"),
            InlineKeyboardButton("❌ نه", callback_data="cancel_send")
        ]
    ]
    
    await message.reply_text(
        f"📨 پیام شما:\n\n{preview}\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "مطمئنی ارسال بشه؟",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def confirm_send(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Confirm and send message"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    state = get_state(user_id)
    
    if state["state"] != STATE_WAITING_CONFIRMATION:
        await query.edit_message_text("❌ خطا: وضعیت نامعتبر")
        return
    
    data = state["data"]
    db = Session()
    
    try:
        # Get sender
        sender = db.query(User).filter(User.telegram_id == user_id).first()
        if not sender:
            await query.edit_message_text("❌ خطا: کاربر یافت نشد")
            return
        
        # Get or create recipient
        recipient = db.query(User).filter(
            User.telegram_id == data["recipient_id"]
        ).first()
        
        if not recipient:
            member_count = db.query(User).count()
            identifier = generate_identifier("Ua", member_count + 1, db)
            
            recipient = User(
                telegram_id=data["recipient_id"],
                username="unknown",
                first_name="Admin",
                identifier=identifier,
                member_number=member_count + 1,
                is_admin=Config.is_admin(data["recipient_id"])
            )
            db.add(recipient)
            db.commit()
            db.refresh(recipient)
        
        # Create message
        anon_msg = AnonymousMessage(
            sender_id=sender.id,
            sender_telegram_id=sender.telegram_id,
            sender_identifier=sender.identifier,
            recipient_id=recipient.id,
            recipient_telegram_id=recipient.telegram_id,
            recipient_identifier=recipient.identifier,
            message_type=data["message_type"],
            message_text=data["message_text"],
            message_file_id=data["file_id"]
        )
        db.add(anon_msg)
        db.commit()
        
        # Send to recipient
        admin_text = f"📩 پیام ناشناس!\n\n👤 از: {sender.identifier}"
        if sender.nickname:
            admin_text += f" ({sender.nickname})"
        admin_text += "\n━━━━━━━━━━━━━━━━━━━━\n\n"
        
        admin_keyboard = [
            [InlineKeyboardButton("💬 پاسخ", callback_data=f"reply_{sender.identifier}")],
            [
                InlineKeyboardButton("🗑️ حذف", callback_data=f"delete_msg_{anon_msg.id}"),
                InlineKeyboardButton("🚫 بلاک", callback_data=f"block_{sender.identifier}")
            ]
        ]
        
        if data["message_type"] == "text":
            await context.bot.send_message(
                chat_id=data["recipient_id"],
                text=admin_text + data["message_text"],
                reply_markup=InlineKeyboardMarkup(admin_keyboard)
            )
        elif data["message_type"] == "photo":
            await context.bot.send_photo(
                chat_id=data["recipient_id"],
                photo=data["file_id"],
                caption=admin_text + (data["message_text"] or ""),
                reply_markup=InlineKeyboardMarkup(admin_keyboard)
            )
        elif data["message_type"] == "voice":
            await context.bot.send_message(
                chat_id=data["recipient_id"],
                text=admin_text
            )
            await context.bot.send_voice(
                chat_id=data["recipient_id"],
                voice=data["file_id"],
                reply_markup=InlineKeyboardMarkup(admin_keyboard)
            )
        
        # Update stats
        sender.total_messages_sent += 1
        recipient.total_messages_received += 1
        db.commit()
        
        # Log
        Log.create_log(
            db=db,
            event_type="message_sent",
            user_id=sender.id,
            telegram_id=sender.telegram_id,
            identifier=sender.identifier,
            action="Sent anonymous message",
            target=recipient.identifier,
            success=True
        )
        
        await query.edit_message_text(
            "✅ پیامت ارسال شد!",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🏠 منوی اصلی", callback_data="back_to_main")
            ]])
        )
        
        clear_state(user_id)
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        await query.edit_message_text(
            "❌ خطا رخ داد",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🏠 منوی اصلی", callback_data="back_to_main")
            ]])
        )
    finally:
        db.close()


async def cancel_send(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel send"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    clear_state(user_id)
    
    from utils.messages import get_main_menu_text
    from utils.keyboards import get_main_menu_keyboard
    
    await query.edit_message_text(
        "❌ لغو شد.\n\n" + get_main_menu_text(),
        reply_markup=get_main_menu_keyboard()
    )
