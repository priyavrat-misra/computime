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
        return requests.get(url).json()

    def send_message(self, msg, chat_id):
        url = (
            f"{self.tg_url}"
            f"sendMessage?chat_id={chat_id}&text={msg}"
            f"&parse_mode=HTML&disable_web_page_preview=True"
        )
        requests.get(url)


bot = chatbot()

usage_text = (
    "Send messages in one of these formats:\u000a"
    "• <code>H:M:S speed</code> <i>(e.g., 3:15:53 2.75)</i>\u000a"
    "• <code>YouTubeVideoURL speed</code>\u000a"
    "• <code>YouTubePlaylistURL speed</code>\u000a\u000a"
)
bug_text = 'Bug? Report it <a href="https://github.com/priyavrat-misra/computime/issues">here</a>.'

dur_pattern = re.compile(r"^[0-9]+:[0-9]+:[0-9]+$")
vd_pattern = re.compile(r"(?<=[=\/&])[a-zA-Z0-9_\-]{11}(?=[=\/&?#\n\r]|$)")
pl_pattern = re.compile(r"^([\S]+list=)?([\w_-]+)[\S]*$")

yt_api = os.getenv("YT")
ytvd_url = f"https://www.googleapis.com/youtube/v3/videos?part=contentDetails&fields=items/contentDetails/duration&key={yt_api}&id="
ytpl_url = f"https://www.googleapis.com/youtube/v3/playlistItems?part=contentDetails&maxResults=50&fields=items/contentDetails/videoId,nextPageToken&key={yt_api}&playlistId="


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
        
        vd_exists = vd_pattern.search(msg)
        pl_exists = pl_pattern.match(msg) if vd_exists is None else None
        if dur_pattern.match(msg):
            h, m, s = tuple(int(x) for x in msg.split(":"))
            dur = datetime.timedelta(hours=h, minutes=m, seconds=s)
        elif vd_exists:
            reply = "The video"
            r = requests.get(f"{ytvd_url}{vd_exists.group()}").json()
            dur = isodate.parse_duration(r["items"][0]["contentDetails"]["duration"])
        elif pl_exists:
            reply = "The playlist"
            pl_id = pl_exists.group(2)
            next_page_token = ""
            while True:
                vd_list = []
                page = requests.get(
                    f"{ytpl_url}{pl_id}&pageToken={next_page_token}"
                ).json()
                for vd in page["items"]:
                    vd_list.append(vd["contentDetails"]["videoId"])
                r = requests.get(f"{ytvd_url}{','.join(vd_list)}").json()
                for vd in r["items"]:
                    dur += isodate.parse_duration(vd["contentDetails"]["duration"])
                if "nextPageToken" in page:
                    next_page_token = page["nextPageToken"]
                else:
                    break
        else:
            raise Exception
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
