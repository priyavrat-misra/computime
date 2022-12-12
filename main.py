import os
import requests
import re
import datetime
import isodate


class chatbot:
    def __init__(self):
        self.tg_url = f'https://api.telegram.org/bot{os.getenv("TG")}/'

    def get_updates(self, offset=None):
        url = self.tg_url + "getUpdates?timeout=100"
        if offset:
            url += f"&offset={offset + 1}"
        r = requests.get(url)
        return r.json()

    def send_message(self, msg, chat_id):
        url = (
            f"{self.tg_url}"
            f"sendMessage?chat_id={chat_id}&text={msg}"
            f"&parse_mode=HTML&disable_web_page_preview=True"
        )
        if msg is not None:
            requests.get(url)


bot = chatbot()

usage_text = (
    "Send messages in one of these formats:\u000a"
    "• <code>h:m:s speed</code>\u000a"
    "• <code>YouTubeVideoURL speed</code>\u000a"
    "<i>E.g., 3:15:53 2.75</i>\u000a\u000a"
)
bug_text = 'Bug? Report it <a href="https://github.com/priyavrat-misra/computime/issues">here</a>.'

dur_pattern = re.compile("^[0-9]+:[0-9]+:[0-9]+$")
video_id = re.compile(r"(?<=[=\/&])[a-zA-Z0-9_\-]{11}(?=[=\/&?#\n\r]|$)")
ytv_url = f'https://www.googleapis.com/youtube/v3/videos?part=contentDetails&key={os.getenv("YT")}&id='


def make_reply(msg):
    if msg == "/start" or msg == "/help":
        return (
            f"{usage_text}"
            "Bot by @prv_t • "
            '<a href="https://github.com/priyavrat-misra/computime">Source code</a>'
        )

    try:
        msg, speed = msg.split()
        speed = float(speed)
        reply = msg
        dur = datetime.timedelta(0)
        if dur_pattern.match(msg):
            h, m, s = tuple(int(x) for x in msg.split(":"))
            dur = datetime.timedelta(hours=h, minutes=m, seconds=s)
        else:
            reply = "The video"
            r = requests.get(f"{ytv_url}{video_id.search(msg).group()}").json()
            dur = isodate.parse_duration(r["items"][0]["contentDetails"]["duration"])
    except:
        return f"Invalid duration or URL.\u000a\u000a{usage_text}{bug_text}"

    result_dur = dur / speed
    return (
        f"{reply} @ {speed}x will take <b>{result_dur}</b>"
        f' and save <b>{"nothing." if speed <= 1 else dur - result_dur}</b>'
    )


update_id = None
while True:
    updates = bot.get_updates(offset=update_id)
    updates = updates["result"]
    if updates:
        for item in updates:
            update_id = item["update_id"]
            if "message" not in item:
                continue
            try:
                message = item["message"]["text"]
            except:
                message = None
            from_ = item["message"]["from"]["id"]
            reply = make_reply(message)
            bot.send_message(reply, from_)

