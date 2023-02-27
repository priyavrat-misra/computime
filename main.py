import os
import requests
import re
import isodate
from datetime import timedelta


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
    "• <code>H:M:S [speed...]</code>\u000a"
    "• <code>YouTube_Video/Playlist_URL [speed...]</code>\u000a"
    "<i>Note:</i> <code>speed(s)</code> is/are optional.\u000a\u000a"
    "<b>Examples:</b>\u000a"
    "• 3:15:53 2.75 2.3 3\u000a"
    "• https://www.youtube.com/playlist?list=PLCiNIjl_KpQhFwQA3G19w1nmhEOlZQsGF\u000a"
    "• https://www.youtube.com/watch?v=dQw4w9WgXcQ 1.6 3.1\u000a\u000a"
)
bug_text = 'Bug? Report it <a href="https://github.com/priyavrat-misra/computime/issues">here</a>.'

dur_pattern = re.compile(r"^[0-9]+:[0-9]+:[0-9]+$")
vd_pattern = re.compile(r"(?<=[=\/&])[a-zA-Z0-9_\-]{11}(?=[=\/&?#\n\r]|$)")
pl_pattern = re.compile(r"^([\S]+list=)?([\w_-]+)[\S]*$")

ytvd_url = f"https://www.googleapis.com/youtube/v3/videos?part=contentDetails&fields=items/contentDetails/duration&key={os.getenv('YT')}&id="
ytpl_url = f"https://www.googleapis.com/youtube/v3/playlistItems?part=contentDetails&maxResults=50&fields=items/contentDetails/videoId,nextPageToken&key={os.getenv('YT')}&playlistId="


def make_reply(msg):
    if msg == "/start" or msg == "/help":
        return (
            f"{usage_text}"
            "Bot by priyavr.at (@prv_t) • "
            '<a href="https://github.com/priyavrat-misra/computime">Source code</a>\u000a'
            '<tg-spoiler><i>If you found the bot helpful, leave it a \u2605 :)</i></tg-spoiler>'
        )

    try:
        params = msg.split()
        msg = params.pop(0)
        speeds = []
        if len(params):
            speeds = map(float, params)
        else:
            speeds = [1, 1.25, 1.5, 1.75, 2]
          
        dur = timedelta(0)
        vd_exists = vd_pattern.search(msg)
        pl_exists = pl_pattern.match(msg) if vd_exists is None else None
        if dur_pattern.match(msg):
            h, m, s = tuple(int(x) for x in msg.split(":"))
            dur = timedelta(hours=h, minutes=m, seconds=s)
            msg = f"<b>{dur}</b>\u000a"
        elif vd_exists:
            vd_id = vd_exists.group()
            msg = f'<a href="https://youtu.be/{vd_id}">This video</a>\u000a'
            r = requests.get(f"{ytvd_url}{vd_id}").json()
            dur = isodate.parse_duration(r["items"][0]["contentDetails"]["duration"])
        elif pl_exists:
            pl_id = pl_exists.group(2)
            msg = f'<a href="{msg}">This playlist</a>\u000a'
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

        for speed in speeds:
            result_dur = dur / speed
            result_dur -= timedelta(microseconds=result_dur.microseconds)
            msg += f"@ <b>{speed:.2f}x = {result_dur}</b>\u000a"
    except:
        return f"Invalid format/URL.\u000a\u000a{usage_text}{bug_text}"
    
    return msg


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
