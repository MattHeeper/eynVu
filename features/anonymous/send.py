from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import Session
from models.user import User
from models.message import AnonymousMessage
from models.log import Log
from utils.state import set_state, get_state, clear_state, STATE_WAITING_MESSAGE, STATE_WAITING_CONFIRMATION
from config import Config


async def start_send_to_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start sending anonymous message to admin"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    set_state(user_id, STATE_WAITING_MESSAGE, {"recipient": "admin"})
    
    await query.edit_message_text(
        "📨 ارسال نامه به عِین\n\n"
        "پیام خود را بفرستید:\n"
        "(متن، عکس، ویس)",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("❌ لغو", callback_data="cancel_send")
        ]])
    )


async def handle_message_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming message from user"""
    user_id = update.effective_user.id
    state = get_state(user_id)
    
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
        "recipient": state["data"]["recipient"],
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
        "مطمئنی که این پیام ارسال بشه؟",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def confirm_send(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Confirm and send anonymous message"""
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
        
        # Get or create admin
        recipient = db.query(User).filter(User.telegram_id == Config.ADMIN_ID).first()
        if not recipient:
            from models.identifier import generate_identifier
            member_count = db.query(User).count()
            identifier = generate_identifier("Ua", member_count + 1, db)
            
            recipient = User(
                telegram_id=Config.ADMIN_ID,
                username="admin",
                first_name="Admin",
                identifier=identifier,
                member_number=member_count + 1,
                is_admin=True
            )
            db.add(recipient)
            db.commit()
            db.refresh(recipient)
        
        # Create message record
        anon_message = AnonymousMessage(
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
        db.add(anon_message)
        db.commit()
        db.refresh(anon_message)
        
        # Prepare admin message
        admin_text = (
            f"📩 پیام ناشناس جدید!\n\n"
            f"👤 از: {sender.identifier}"
        )
        if sender.nickname:
            admin_text += f" ({sender.nickname})"
        admin_text += "\n━━━━━━━━━━━━━━━━━━━━\n\n"
        
        # Admin keyboard
        admin_keyboard = [
            [InlineKeyboardButton("💬 پاسخ", callback_data=f"reply_{sender.identifier}")],
            [
                InlineKeyboardButton("🗑️ حذف", callback_data=f"delete_msg_{anon_message.id}"),
                InlineKeyboardButton("🚫 بلاک", callback_data=f"block_{sender.identifier}")
            ]
        ]
        
        # Send to admin based on message type
        if data["message_type"] == "text":
            admin_msg = await context.bot.send_message(
                chat_id=Config.ADMIN_ID,
                text=admin_text + data["message_text"],
                reply_markup=InlineKeyboardMarkup(admin_keyboard)
            )
        elif data["message_type"] == "photo":
            admin_msg = await context.bot.send_photo(
                chat_id=Config.ADMIN_ID,
                photo=data["file_id"],
                caption=admin_text + (data["message_text"] or ""),
                reply_markup=InlineKeyboardMarkup(admin_keyboard)
            )
        elif data["message_type"] == "voice":
            await context.bot.send_message(
                chat_id=Config.ADMIN_ID,
                text=admin_text
            )
            admin_msg = await context.bot.send_voice(
                chat_id=Config.ADMIN_ID,
                voice=data["file_id"],
                reply_markup=InlineKeyboardMarkup(admin_keyboard)
            )
        
        # Update message with admin message_id
        anon_message.recipient_message_id = admin_msg.message_id
        db.commit()
        
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
        
        # Confirm to sender
        await query.edit_message_text(
            "✅ پیامت با موفقیت به صورت ناشناس ارسال شد!",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🏠 منوی اصلی", callback_data="back_to_main")
            ]])
        )
        
        clear_state(user_id)
        
    except Exception as e:
        print(f"Error sending message: {e}")
        await query.edit_message_text(
            "❌ خطایی رخ داد. لطفاً دوباره تلاش کنید.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🏠 منوی اصلی", callback_data="back_to_main")
            ]])
        )
    finally:
        db.close()


async def cancel_send(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel sending message"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    clear_state(user_id)
    
    from utils.messages import get_main_menu_text
    from utils.keyboards import get_main_menu_keyboard
    
    await query.edit_message_text(
        "❌ ارسال پیام لغو شد.\n\n" + get_main_menu_text(),
        reply_markup=get_main_menu_keyboard()
    )
