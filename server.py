from bot import chatbot

bot = chatbot("./config.cfg")

def make_reply(msg):
    if msg == "/start":
        return 'Send messages with the format:\u000a'\
                '<code>hrs:mins:secs speed</code>\u000a'\
                '<i>E.g., 3:15:53 2.75</i>\u000a\u000a'\
                '<a href="tg://user?id=1766203429">Author</a> • '\
                '<a href="https://github.com/priyavrat-misra/computime">Code</a>'
    try:
        dur, speed = msg.split()
        speed = float(speed)
        h, m, s = tuple(int(x) for x in dur.split(':'))
        t1 = (h * 3600 + m * 60 + s)
        t2 = t1 - (t1 / speed)
        t1 /= speed
        h, m, s = computime(t1)
        msg = f"<b>{dur}</b> @ <b>{speed}x</b> will take <b>{h}:{m}:{s:.2f}</b>"
        h, m, s = computime(t2)
        msg += f" and save <b>{h}:{m}:{s:.2f}</b>"
        return msg
    except:
        return "Invalid format."

def computime(time):
    '''
    converts time in seconds to time in hours, minutes and seconds
    '''
    h = int(time / 3600)
    m = int((time - h * 3600) / 60)
    s = time - h * 3600 - m * 60
    return h, m, s

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

