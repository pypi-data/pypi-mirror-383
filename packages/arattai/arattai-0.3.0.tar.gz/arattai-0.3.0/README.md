from ArattaiBot import ArattaiBot, Bot

ArattaiBot = ArattaiBot(isShowQr=True)
bot = ArattaiBot.login_with_qr()
chats = bot.fetch_chats(limit=500)
print(chats)
bot.sender.send_message("Message",chat=chats["chat_id"])
bot.sender.send_message("Message",chat_id="2343453654645_chat_id")
bot.sender.send_file("file.extension","Caption",chat=chats["chat_id"])
bot.sender.send_file("file.extension","Caption",chat_id="2343453654645_chat_id")
