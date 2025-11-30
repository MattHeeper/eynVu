import logging
import os
from flask import Flask, request
from telegram import Update
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

# Flask app for webhook
app = Flask(__name__)

# Global bot application
bot_application = None


def setup_application():
    """Setup bot application"""
    global bot_application
    
    # Create application
    bot_application = Application.builder().token(Config.BOT_TOKEN).build()
    
    # Add handlers
    bot_application.add_handler(CommandHandler("start", start_command))
    bot_application.add_handler(CommandHandler("menu", menu_command))
    bot_application.add_handler(CallbackQueryHandler(handle_main_menu_callback))
    
    return bot_application


@app.route('/')
def index():
    """Health check endpoint"""
    return {
        "status": "running",
        "bot": Config.BOT_NAME,
        "version": Config.BOT_VERSION
    }


@app.route(f'/{Config.BOT_TOKEN}', methods=['POST'])
def webhook():
    """Handle incoming updates from Telegram"""
    try:
        # Get update from request
        update = Update.de_json(request.get_json(force=True), bot_application.bot)
        
        # Process update in async context
        import asyncio
        asyncio.run(bot_application.process_update(update))
        
        return 'ok'
    except Exception as e:
        logger.error(f"Error processing update: {e}")
        return 'error', 500


def main():
    """Main function"""
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
    
    # Setup bot application
    global bot_application
    bot_application = setup_application()
    
    # Initialize bot
    import asyncio
    asyncio.run(bot_application.initialize())
    asyncio.run(bot_application.start())
    
    # Get webhook URL from environment (Render provides this)
    webhook_url = os.getenv('RENDER_EXTERNAL_URL')
    if webhook_url:
        webhook_url = f"{webhook_url}/{Config.BOT_TOKEN}"
        asyncio.run(bot_application.bot.set_webhook(url=webhook_url))
        print(f"\n✅ Webhook set to: {webhook_url}")
    else:
        print("\n⚠️  No RENDER_EXTERNAL_URL found, webhook not set")
    
    print("\n🚀 Bot is ready!")
    print(f"📡 Listening on port {os.getenv('PORT', 10000)}\n")
    
    # Run Flask app
    port = int(os.getenv('PORT', 10000))
    app.run(host='0.0.0.0', port=port)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Bot stopped by user")
    except Exception as e:
        logger.error(f"Critical error: {e}")
        print(f"\n❌ Critical error: {e}")
