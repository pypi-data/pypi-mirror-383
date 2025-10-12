# 🤖 EasyAiogram

**EasyAiogram** is a beginner-friendly wrapper for the [Aiogram](https://docs.aiogram.dev/) framework.  
It simplifies creating Telegram bots by making commands, inline buttons, and callbacks effortless — no boilerplate, no async headaches.

---

## 🚀 Features

✅ Create bots with **just a few lines**  
✅ Add **commands** easily  
✅ Build **inline keyboards** with a simple `.append()` chain  
✅ Handle **callbacks** without extra setup  
✅ Clean, object-oriented API — perfect for both beginners and small projects

---

## 🧩 Installation

```bash
pip install aiogram
pip install easyaiogram


# Example usage

```bash
from easy_aiogram import EasyAiogram

bot = EasyAiogram("YOUR_BOT_TOKEN")

# Create an inline keyboard
main_key = bot.createinkey("main").append("Press me", "pressed")

# Register a command
bot.makecommand("/start", "Welcome to Easy Aiogram!", main_key)

# Handle the callback
bot.oncallback("pressed", "You pressed the button!")

# Start the bot
bot.startbot()
```