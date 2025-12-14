import logging
import os
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from config import Config
from database import init_db, test_connection
from handlers.start import start_command
from handlers.menu import menu_command, handle_main_menu_callback
from handlers.rules import rules_command, rule_as_command, show_rule_as, back_to_rules, close_rules
from features.anonymous.send import (
    start_send_to_admin,
    start_send_to_admins,
    start_send_to_user,
    start_send_to_specific,
    handle_message_input,
    confirm_send,
    cancel_send
)

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=getattr(logging, Config.LOG_LEVEL)
)
logger = logging.getLogger(__name__)

# Flask app
app = Flask(__name__)

# Initialize database on startup
print("=" * 50)
print(f"🤖 Starting {Config.BOT_NAME} Bot v{Config.BOT_VERSION}")
print("=" * 50)

if not test_connection():
    logger.error("Failed to connect to database. Exiting...")
    exit(1)

if not init_db():
    logger.error("Failed to initialize database. Exiting...")
    exit(1)

print("\n✅ Database ready!")
print(f"🔑 Admin ID: {Config.ADMIN_ID}")

# setup bot application
bot_application = Application.builder().token(Config.BOT_TOKEN).build()

# Add handlers
bot_application.add_handler(CommandHandler("start", start_command))
bot_application.add_handler(CommandHandler("menu", menu_command))
bot_application.add_handler(CommandHandler("rules", rules_command))
bot_application.add_handler(CommandHandler("rule_as", rule_as_command))

# Main menu callback handler
bot_application.add_handler(CallbackQueryHandler(
    handle_main_menu_callback,
    pattern="^(back_to_main|send_letter|cafe_menu|leaderboard|lists|social_media|my_profile)$"
))

# Anonymous message handlers
bot_application.add_handler(CallbackQueryHandler(start_send_to_admin, pattern="^send_to_admin$"))
bot_application.add_handler(CallbackQueryHandler(start_send_to_admins, pattern="^send_to_admins$"))
bot_application.add_handler(CallbackQueryHandler(start_send_to_user, pattern="^send_to_user$"))
bot_application.add_handler(CallbackQueryHandler(start_send_to_specific, pattern="^send_to_specific_"))
bot_application.add_handler(CallbackQueryHandler(confirm_send, pattern="^confirm_send$"))
bot_application.add_handler(CallbackQueryHandler(cancel_send, pattern="^cancel_send$"))

# Rules handlers
bot_application.add_handler(CallbackQueryHandler(show_rule_as, pattern="^rule_as$"))
bot_application.add_handler(CallbackQueryHandler(back_to_rules, pattern="^back_to_rules$"))
bot_application.add_handler(CallbackQueryHandler(close_rules, pattern="^close_rules$"))

# Message handler (must be last!)
bot_application.add_handler(MessageHandler(
    filters.TEXT | filters.PHOTO | filters.VOICE,
    handle_message_input
))

print("✅ Handlers registered")

# Initialize bot
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

try:
    loop.run_until_complete(bot_application.initialize())
    loop.run_until_complete(bot_application.start())
    print("✅ Bot initialized")
    
    # Set webhook
    webhook_url = os.getenv('RENDER_EXTERNAL_URL')
    if webhook_url:
        webhook_url = f"{webhook_url}/{Config.BOT_TOKEN}"
        loop.run_until_complete(bot_application.bot.set_webhook(url=webhook_url))
        print(f"✅ Webhook set to: {webhook_url}")
    else:
        print("⚠️  No RENDER_EXTERNAL_URL found")
        
    print("🚀 Bot is ready!\n")
except Exception as e:
    logger.error(f"Failed to initialize bot: {e}")
    exit(1)


@app.route('/')
def index():
    """Health check endpoint"""
    return {
        "status": "running",
        "bot": Config.BOT_NAME,
        "version": Config.BOT_VERSION
    }


@app.route('/migrate')
def run_migration():
    """Run database migration - visit this URL once to add share_code column"""
    try:
        from sqlalchemy import text
        from utils.share_code import generate_share_code, is_share_code_unique
        
        db = Session()
        
        # Check if column exists
        check_query = text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='users' AND column_name='share_code';
        """)
        
        result = db.execute(check_query).fetchone()
        
        if result:
            db.close()
            return {"status": "already_migrated", "message": "share_code column already exists!"}
        
        # Add column
        alter_query = text("ALTER TABLE users ADD COLUMN share_code VARCHAR(9) NULL;")
        db.execute(alter_query)
        db.commit()
        
        # Add index
        index_query = text("CREATE INDEX ix_users_share_code ON users (share_code);")
        db.execute(index_query)
        db.commit()
        
        # Generate share codes for existing users
        from models.user import User
        users = db.query(User).filter(
            (User.share_code == None) | (User.share_code == '')
        ).all()
        
        for user in users:
            user_share_code = generate_share_code()
            while not is_share_code_unique(user_share_code, db):
                user_share_code = generate_share_code()
            user.share_code = user_share_code
        
        db.commit()
        
        # Add unique constraint
        constraint_query = text("ALTER TABLE users ADD CONSTRAINT uq_users_share_code UNIQUE (share_code);")
        db.execute(constraint_query)
        db.commit()
        
        db.close()
        
        return {
            "status": "success",
            "message": "Migration completed successfully!",
            "users_updated": len(users)
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }, 500


@app.route(f'/{Config.BOT_TOKEN}', methods=['POST'])
def webhook():
    """Handle incoming updates from Telegram"""
    try:
        # Get update from request
        update_data = request.get_json(force=True)
        update = Update.de_json(update_data, bot_application.bot)
        
        # Process update in async context
        asyncio.run(bot_application.process_update(update))
        
        return 'ok'
    except Exception as e:
        logger.error(f"Error processing update: {e}", exc_info=True)
        return 'error', 500


if __name__ == "__main__":
    port = int(os.getenv('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
