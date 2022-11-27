import requests
import json
import configparser as cfg

class chatbot():
    def __init__(self, config):
        self.token = self.get_token_from_file(config)
        self.base_url = f"https://api.telegram.org/bot{self.token}/"

    def get_updates(self, offset=None):
        url = self.base_url + "getUpdates?timeout=100"
        if offset:
            url += f"&offset={offset + 1}"
        r = requests.get(url)
        return json.loads(r.content)

    def send_message(self, msg, chat_id):
        url = self.base_url + f"sendMessage?chat_id={chat_id}&text={msg}&parse_mode=HTML&disable_web_page_preview=True"
        if msg is not None:
            requests.get(url)

    def get_token_from_file(self, config):
        parser = cfg.ConfigParser()
        parser.read(config)
        return parser.get('creds', 'token')

