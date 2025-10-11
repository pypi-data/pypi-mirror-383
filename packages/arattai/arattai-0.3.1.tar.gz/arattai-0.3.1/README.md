```python
from ArattaiBot import ArattaiBot, Bot

# Initialize the bot and show QR for login
ArattaiBot = ArattaiBot(isShowQr=True)

# Login using QR
bot = ArattaiBot.login_with_qr()

# Fetch chats (limit to 500)
chats = bot.fetch_chats(limit=500)
print(chats)

# Send a text message to a chat (using chat object)
bot.sender.send_message("Message", chat=chats["chat_id"])

# Send a text message to a specific chat ID
bot.sender.send_message("Message", chat_id="2343453654645_chat_id")

# Send a file with caption to a chat (using chat object)
bot.sender.send_file("file.extension", "Caption", chat=chats["chat_id"])

# Send a file with caption to a specific chat ID
bot.sender.send_file("file.extension", "Caption", chat_id="2343453654645_chat_id")
```