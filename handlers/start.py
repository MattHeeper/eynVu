from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from database import Session
from models.user import User
from models.log import Log
from models.identifier import generate_identifier
from utils.share_code import generate_share_code, is_share_code_unique
from utils.keyboards import get_main_menu_keyboard
from utils.messages import get_welcome_message, get_main_menu_text
from utils.state import set_state, STATE_WAITING_MESSAGE


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle /start command
    Register new user or show main menu for existing user
    Also handles share links: /start {share_code}
    """
    user = update.effective_user
    db = Session()
    
    try:
        # Check if there's a share code
        share_code = None
        if context.args and len(context.args) > 0:
            share_code = context.args[0]
        
        # Check if user exists
        existing_user = db.query(User).filter(
            User.telegram_id == user.id
        ).first()
        
        # Handle share link
        if share_code and existing_user:
            await handle_share_link(update, context, existing_user, share_code, db)
            return
        
        if existing_user:
            # Existing user - show main menu
            await update.message.reply_text(
                get_main_menu_text(),
                reply_markup=get_main_menu_keyboard()
            )
            
            # Update last activity
            from sqlalchemy import text
            existing_user.last_activity = db.execute(text("SELECT NOW()")).scalar()
            db.commit()
            
        else:
            # New user - register
            member_count = db.query(User).count()
            member_number = member_count + 1
            
            # Generate unique identifier
            identifier = generate_identifier("Ua", member_number, db)
            
            # Generate share code
            user_share_code = generate_share_code()
            while not is_share_code_unique(user_share_code, db):
                user_share_code = generate_share_code()
            
            # Create new user
            new_user = User(
                telegram_id=user.id,
                username=user.username,
                first_name=user.first_name,
                last_name=user.last_name,
                identifier=identifier,
                share_code=user_share_code,
                member_number=member_number
            )
            
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            
            # Log the registration
            Log.create_log(
                db=db,
                event_type="user_join",
                user_id=new_user.id,
                telegram_id=user.id,
                identifier=identifier,
                action="User registered to bot",
                success=True
            )
            
            # Send welcome message
            welcome_text = get_welcome_message(
                user_name=user.first_name,
                identifier=identifier,
                member_number=member_number
            )
            
            await update.message.reply_text(
                welcome_text,
                reply_markup=get_main_menu_keyboard()
            )
            
            print(f"✅ New user registered: {identifier} (#{member_number})")
            
            # If came from share link, start send flow
            if share_code:
                await handle_share_link(update, context, new_user, share_code, db)
            
    except Exception as e:
        print(f"❌ Error in start_command: {e}")
        import traceback
        traceback.print_exc()
        await update.message.reply_text(
            "❌ خطایی رخ داد. لطفاً دوباره تلاش کنید."
        )
    finally:
        db.close()


async def handle_share_link(update: Update, context: ContextTypes.DEFAULT_TYPE, 
                            current_user: User, share_code: str, db):
    """Handle incoming share link"""
    try:
        # Find target user by share_code
        target_user = db.query(User).filter(User.share_code == share_code).first()
        
        if not target_user:
            await update.message.reply_text(
                "❌ لینک نامعتبر است یا منقضی شده",
                reply_markup=get_main_menu_keyboard()
            )
            return
        
        # Check if trying to send to self
        if target_user.telegram_id == current_user.telegram_id:
            await update.message.reply_text(
                "❌ نمی‌توانید به خودتان پیام ناشناس ارسال کنید!",
                reply_markup=get_main_menu_keyboard()
            )
            return
        
        # Set state for sending message
        set_state(current_user.telegram_id, STATE_WAITING_MESSAGE, {
            "recipient": "user",
            "recipient_id": target_user.telegram_id,
            "recipient_identifier": target_user.identifier
        })
        
        display_name = target_user.nickname or target_user.first_name
        
        await update.message.reply_text(
            f"📨 ارسال پیام ناشناس به {display_name}\n\n"
            f"پیام خود را ارسال کنید:",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("❌ لغو", callback_data="cancel_send")
            ]])
        )
        
    except Exception as e:
        print(f"❌ Error in handle_share_link: {e}")
        import traceback
        traceback.print_exc()
