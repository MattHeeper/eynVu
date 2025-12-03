from telegram import Update
from telegram.ext import ContextTypes
from database import Session
from models.user import User
from models.log import Log
from models.identifier import generate_identifier
from utils.keyboards import get_main_menu_keyboard
from utils.messages import get_welcome_message, get_main_menu_text


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle /start command
    Register new user or show main menu for existing user
    """
    user = update.effective_user
    db = Session()
    
    try:
        # Check if user exists
        existing_user = db.query(User).filter(
            User.telegram_id == user.id
        ).first()
        
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
            # Get member number (count + 1)
            member_count = db.query(User).count()
            member_number = member_count + 1
            
            # Generate unique identifier
            identifier = generate_identifier("Ua", member_number, db)
            
            # Create new user
            new_user = User(
                telegram_id=user.id,
                username=user.username,
                first_name=user.first_name,
                last_name=user.last_name,
                identifier=identifier,
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
            
    except Exception as e:
        print(f"❌ Error in start_command: {e}")
        await update.message.reply_text(
            "❌ خطایی رخ داد. لطفاً دوباره تلاش کنید."
        )
    finally:
        db.close()
