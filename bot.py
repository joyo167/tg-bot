import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import requests
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Initialize logger
logger = logging.getLogger(__name__)

# Get API tokens from environment variables
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
AI_API_KEY = os.environ.get("AI_API_KEY")  # This could be for OpenAI or any other free AI service

# Command handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_text(
        f"Hi {user.first_name}! I'm your AI assistant. How can I help you today?"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text(
        "I'm an AI assistant bot. Just send me a message and I'll respond!"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Process user messages and get AI responses."""
    user_message = update.message.text
    chat_id = update.effective_chat.id
    
    # Show "typing..." indicator
    await context.bot.send_chat_action(chat_id=chat_id, action="typing")
    
    try:
        # Get AI response (this example uses a free alternative to OpenAI's API)
        ai_response = get_ai_response(user_message)
        
        # Send the AI response back to the user
        await update.message.reply_text(ai_response)
    
    except Exception as e:
        logger.error(f"Error getting AI response: {e}")
        await update.message.reply_text(
            "Sorry, I encountered an error processing your request. Please try again later."
        )

def get_ai_response(user_message: str) -> str:
    """
    Function to get AI response using a free AI API.
    This is a placeholder - replace with your chosen AI API implementation.
    """
    # Option 1: Using a free AI API service (example with HuggingFace Inference API)
    # There are multiple free options you can implement here
    
    # Example with HuggingFace API (they offer a free tier)
    API_URL = "https://api-inference.huggingface.co/models/facebook/blenderbot-400M-distill"
    headers = {"Authorization": f"Bearer {AI_API_KEY}"}
    
    payload = {"inputs": user_message}
    response = requests.post(API_URL, headers=headers, json=payload)
    
    if response.status_code == 200:
        return response.json()[0]["generated_text"]
    else:
        # Fallback response if API call fails
        return "I'm sorry, I couldn't process that request right now. Please try again later."

def run_health_server():
    class HealthHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'Bot is running!')
    
    server = HTTPServer(('0.0.0.0', int(os.environ.get('PORT', 8080))), HealthHandler)
    server.serve_forever()

def main() -> None:
    """Start the bot."""
    # Create the Application
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    # Add message handler
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start health check server
    threading.Thread(target=run_health_server, daemon=True).start()
    
    # Start the Bot
    application.run_polling()

if __name__ == "__main__":
    main()
