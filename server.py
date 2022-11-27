from bot import chatbot

bot = chatbot("./config.cfg")

def make_reply(msg):
    if msg == "/start":
        return "Send messages with the format <code>hrs:mins:secs speed</code> else get ignored. ¯\_(ツ)_/¯\u000a\u000a<i>E.g., 3:15:53 2.75</i>"
    return msg

update_id = None
while True:
    updates = bot.get_updates(offset=update_id)
    updates = updates["result"]
    if updates:
        for item in updates:
            update_id = item["update_id"]
            try:
                message = item["message"]["text"]
            except:
                message = None
            from_ = item["message"]["from"]["id"]
            reply = make_reply(message)
            bot.send_message(reply, from_)

