import logging
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from config import Config
from database import init_db, test_connection
from handlers.start import start_command
from handlers.menu import menu_command, handle_main_menu_callback

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=getattr(logging, Config.LOG_LEVEL)
)
logger = logging.getLogger(__name__)


def main():
    """
    Main function to run the bot
    """
    print("=" * 50)
    print(f"🤖 Starting {Config.BOT_NAME} Bot v{Config.BOT_VERSION}")
    print("=" * 50)
    
    # Test database connection
    if not test_connection():
        logger.error("Failed to connect to database. Exiting...")
        return
    
    # Initialize database tables
    if not init_db():
        logger.error("Failed to initialize database. Exiting...")
        return
    
    print("\n✅ Database ready!")
    print(f"🔑 Admin ID: {Config.ADMIN_ID}")
    print("\n🚀 Starting bot...\n")
    
    # Create application
    application = Application.builder().token(Config.BOT_TOKEN).build()
    
    # Add handlers
    # Commands
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("menu", menu_command))
    
    # Callback queries
    application.add_handler(CallbackQueryHandler(handle_main_menu_callback))
    
    # Start bot
    print("✅ Bot is running!")
    print("Press Ctrl+C to stop\n")
    
    application.run_polling(allowed_updates=["message", "callback_query"])


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Bot stopped by user")
    except Exception as e:
        logger.error(f"Critical error: {e}")
        print(f"\n❌ Critical error: {e}")
