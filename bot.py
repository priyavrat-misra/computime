import os
import requests

class chatbot():
    def __init__(self):
        self.tg_api = os.getenv('TG')
        self.tg_url = f'https://api.telegram.org/bot{self.tg_api}/'

    def get_updates(self, offset=None):
        url = self.tg_url + 'getUpdates?timeout=100'
        if offset:
            url += f'&offset={offset + 1}'
        r = requests.get(url)
        return r.json()

    def send_message(self, msg, chat_id):
        url = (f'{self.tg_url}'
               f'sendMessage?chat_id={chat_id}&text={msg}'
               f'&parse_mode=HTML&disable_web_page_preview=True')
        if msg is not None:
            requests.get(url)

