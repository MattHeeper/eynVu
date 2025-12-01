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
    # Create application
    application = Application.builder().token(Config.BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("menu", menu_command))
    application.add_handler(CallbackQueryHandler(handle_main_menu_callback))
    
    logger.info("✅ Handlers registered")
    
    return application


@app.route('/')
def index():
    """Health check endpoint"""
    return {
        "status": "running",
        "bot": Config.BOT_NAME,
        "version": Config.BOT_VERSION
    }


@app.route(f'/{Config.BOT_TOKEN}', methods=['POST'])
async def webhook():
    """Handle incoming updates from Telegram"""
    try:
        # Get update from request
        update = Update.de_json(request.get_json(force=True), bot_application.bot)
        
        # Process update
        await bot_application.process_update(update)
        
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
    
    # Initialize bot using asyncio
    import asyncio
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    loop.run_until_complete(bot_application.initialize())
    loop.run_until_complete(bot_application.start())
    
    # Get webhook URL from environment
    webhook_url = os.getenv('RENDER_EXTERNAL_URL')
    if webhook_url:
        webhook_url = f"{webhook_url}/{Config.BOT_TOKEN}"
        loop.run_until_complete(bot_application.bot.set_webhook(url=webhook_url))
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
