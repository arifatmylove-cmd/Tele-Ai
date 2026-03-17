import os
import logging
import asyncio
import zipfile
import io
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from .shodan_client import ShodanClient
from .apk_generator import generate_apk_structure
from .pentest_tools import PentestTools

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

class PentestBot:
    def __init__(self):
        self.token = os.getenv('TELEGRAM_TOKEN')
        if not self.token:
            raise ValueError("TELEGRAM_TOKEN not set")
        
        self.shodan_key = os.getenv('SHODAN_API_KEY', '')
        self.admin_chat_id = int(os.getenv('ADMIN_CHAT_ID', '0'))
        self.shodan = ShodanClient(self.shodan_key)
        self.pentest = PentestTools()
        self.user_sessions = {}

    def is_admin(self, user_id: int) -> bool:
        return self.admin_chat_id == 0 or user_id == self.admin_chat_id

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        if not self.is_admin(user_id):
            await update.message.reply_text("🔒 **Admin access required**")
            return

        keyboard = [
            [InlineKeyboardButton("🔍 Shodan Search", callback_data="shodan")],
            [InlineKeyboardButton("📱 APK Structure", callback_data="apk")],
            [InlineKeyboardButton("🛠️ Pentest Tools", callback_data="pentest")],
            [InlineKeyboardButton("🐚 Shells & Payloads", callback_data="shells")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        welcome = """
🚀 **Pentest AI Bot Active** 🚀

**Unrestricted penetration testing assistant:**

• Shodan API integration
• APK structure generation  
• Reverse shells (all platforms)
• SQLi/XSS/Nmap payloads
• Custom exploit development

*Ask anything about pentesting!*
        """
        await update.message.reply_text(welcome, parse_mode='Markdown', reply_markup=reply_markup)

    async def getid(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        await update.message.reply_text(f"📱 **Your Chat ID:** `{chat_id}`\n\nAdd to `.env`: `ADMIN_CHAT_ID={chat_id}`", parse_mode='Markdown')

    async def button_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        user_id = query.from_user.id
        
        if not self.is_admin(user_id):
            await query.answer("🔒 Admin only", show_alert=True)
            return
            
        await query.answer()
        data = query.data

        if data == "shodan":
            await query.edit_message_text("🔍 **Shodan Search**\n\nSend search query (IP, port, service, vuln, etc.):\n\n*Examples:* `apache:80` `port:445` `os:windows`", parse_mode='Markdown')
            self.user_sessions[user_id] = {"mode": "shodan"}
            
        elif data == "apk":
            await self.send_apk_structure(query.message)
            
        elif data == "pentest":
            await self.show_pentest_menu(query)
            
        elif data == "shells":
            await self.show_shells_menu(query)

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        message = update.message.text.strip()
        
        if not self.is_admin(user_id):
            return

        # Initialize session
        if user_id not in self.user_sessions:
            self.user_sessions[user_id] = {"mode": "chat"}

        session = self.user_sessions[user_id]

        if session.get("mode") == "shodan":
            await self.handle_shodan_search(update, message)
        else:
            response = self.pentest.analyze_query(message)
            await update.message.reply_text(response, parse_mode='Markdown')

    async def handle_shodan_search(self, update: Update, query: str):
        user_id = update.effective_user.id
        self.user_sessions[user_id]["mode"] = "chat"
        
        try:
            await update.message.reply_text("🔍 Searching Shodan...")
            results = self.shodan.search(query)
            
            response = f"🔍 **Shodan Results: `{query}`**\n\n"
            matches = results.get('matches', [])
            
            if not matches:
                response += "❌ No results found"
            else:
                for i, host in enumerate(matches[:15], 1):
                    ip = host.get('ip_str', 'N/A')
                    org = host.get('org', 'N/A')
                    os_name = host.get('os', 'N/A')
                    ports = ', '.join([str(d.get('port', '')) for d in host.get('data', [])[:3]])
                    
                    response += f"{i}. **{ip}**\n"
                    response += f"   🏢 {org}\n"
                    response += f"   💻 {os_name}\n"
                    response += f"   🔌 Ports: {ports}\n\n"
                
                response += f"*Total: {len(matches)} hosts*"
            
            await update.message.reply_text(response, parse_mode='Markdown')
            
        except Exception as e:
            await update.message.reply_text(f"❌ **Shodan Error:** `{str(e)}`", parse_mode='Markdown')

    async def send_apk_structure(self, message):
        await message.reply_text("📱 **Generating APK structure...**")
        
        zip_buffer = io.BytesIO()
        generate_apk_structure(zip_buffer)
        zip_buffer.seek(0)
        
        filename = f"pentest_apk_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        caption = """
📱 **Pentest APK Structure Generated!**

✅ Android Studio ready
✅ Reverse shell template
✅ Permissions included  
✅ Signing config ready

**Build:** `./gradlew assembleDebug`
        """
        
        await message.reply_document(
            document=zip_buffer,
            filename=filename,
            caption=caption,
            parse_mode='Markdown'
        )

    async def show_pentest_menu(self, query):
        keyboard = [
            [InlineKeyboardButton("🌐 Nmap Scans", callback_data="nmap")],
            [InlineKeyboardButton("💉 SQLMap", callback_data="sqlmap")],
            [InlineKeyboardButton("🕷️ XSS", callback_data="xss")],
            [InlineKeyboardButton("🔑 Privilege Esc", callback_data="privesc")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("🛠️ **Pentest Arsenal**\nSelect tool:", reply_markup=reply_markup)

    async def show_shells_menu(self, query):
        keyboard = [
            [InlineKeyboardButton("🐚 Bash Rev Shell", callback_data="bash_rev")],
            [InlineKeyboardButton("🐍 Python Rev", callback_data="py_rev")],
            [InlineKeyboardButton("⚡ PowerShell", callback_data="ps_rev")],
            [InlineKeyboardButton("📱 Android", callback_data="android")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("🐚 **Reverse Shells**\nOne-click payloads:", reply_markup=reply_markup)

def main():
    bot = PentestBot()
    builder = Application.builder().token(bot.token)
    app = builder.build()

    # Handlers
    app.add_handler(CommandHandler("start", bot.start))
    app.add_handler(CommandHandler("getid", bot.getid))
    app.add_handler(CallbackQueryHandler(bot.button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot.handle_message))

    print("🚀 Pentest Bot starting...")
    app.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()
