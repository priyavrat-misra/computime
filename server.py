import time
from bot import chatbot

bot = chatbot("./config.cfg")

def make_reply(msg):
    if msg == "/start":
        return 'Send messages with the format:\u000a'\
                '<code>hrs:mins:secs speed</code>\u000a'\
                '<i>E.g., 3:15:53 2.75</i>\u000a\u000a'\
                'by @prv_t • '\
                '<a href="https://github.com/priyavrat-misra/computime">Source code</a>'
    try:
        dur, speed = msg.split()
        speed = float(speed)
        h, m, s = tuple(int(x) for x in dur.split(':'))
        t1 = ((h % 24) * 3600 + m * 60 + s)
        t2 = t1 - (t1 / speed)
        t1 /= speed
        msg = f"<b>{dur}</b> @ <b>{speed}x</b> will take <b>{computime(t1)}</b>"
        msg += f" and save <b>{computime(t2)}</b>"
        return msg
    except:
        return "Invalid format."

def computime(secs):
    '''
    converts time in seconds to time in hours, minutes and seconds
    '''
    return time.strftime("%H:%M:%S", time.gmtime(secs))

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

