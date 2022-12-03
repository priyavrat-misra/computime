import datetime
from bot import chatbot

bot = chatbot('./config.cfg')

def make_reply(msg):
    usage = ('Send messages in this format:\u000a'
            '<code>hrs:mins:secs speed</code>\u000a'
            '<i>E.g., 3:15:53 2.75</i>\u000a\u000a')

    if msg == "/start" or msg == "/help":
        return (f'{usage}'
                'Bot by @prv_t • '
                '<a href="https://github.com/priyavrat-misra/computime">Source code</a>')
    try:
        dur, speed = msg.split()
        speed = float(speed)
        h, m, s = tuple(int(x) for x in dur.split(':'))
        t1 = t2 = h * 3600 + m * 60 + s
        t1 /= speed
        t2 -= t1
        return (f'<b>{dur}</b> @ <b>{speed}x</b>'
               f' will take <b>{datetime.timedelta(seconds=t1)}</b>'
               f' and save <b>{"nothing." if speed <= 1 else datetime.timedelta(seconds=t2)}</b>')
    except:
        return ('Invalid input.\u000a\u000a'
                f'{usage}'
                'Bug? Report it '
                '<a href="https://github.com/priyavrat-misra/computime/issues">here</a>.')

update_id = None
while True:
    updates = bot.get_updates(offset=update_id)
    updates = updates['result']
    if updates:
        for item in updates:
            update_id = item['update_id']
            if 'message' not in item:
                continue
            try:
                message = item['message']['text']
            except:
                message = None
            from_ = item['message']['from']['id']
            reply = make_reply(message)
            bot.send_message(reply, from_)

