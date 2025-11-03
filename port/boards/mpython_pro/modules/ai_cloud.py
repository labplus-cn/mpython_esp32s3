import binascii
import json
import os

import requests

from mpython import *

# 语音文件转汉字api key
API_KEY = "UiMsouhTOzHYmaWS1beQLA2w"
SECRET_KEY = "ZKBZCgLtazS4Hqzk5OO7OL0GKNA2wTLO"

# 文心3.5 8K模型api key
API_KEY_chat = "1EgOD1zSJHMjm9XjxrxWRtD9"
SECRET_KEY_chat = "gHRZmcknwujyf0xFMYRCq2fTQRUiBBYP"


def get_access_token(API_KEY, SECRET_KEY):
    url = "https://aip.baidubce.com/oauth/2.0/token"
    params = "grant_type=client_credentials&client_id={}&client_secret={}".format(API_KEY, SECRET_KEY)
    response = requests.post(url + "?" + params)
    token = response.json().get("access_token", "")
    response.close()
    return token


def file_to_base64(filename):
    with open(filename, "rb") as f:
        data = f.read()
    return binascii.b2a_base64(data).strip()


def get_file_size(filename):
    return os.stat(filename)[6]


class AI:
    def __init__(self, url):
        self.url = url
        self.payload = None
        self.headers = None

    def set_payload(self, payload):
        self.payload = payload

    def set_headers(self, headers):
        self.headers = headers

    def request_ai(self):
        url = self.url

        if self.payload is None:
            print("Error：请设置ai参数")
            return
        payload = json.dumps(self.payload)

        if self.headers is None:
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
        else:
            headers = self.headers

        response = requests.request("POST", url, headers=headers, data=payload.encode("utf-8"))
        return response

    @classmethod
    def get_text(cls, filename="vad_record.pcm", audio_format="pcm", rate=16000, channel=1):
        url = "https://vop.baidu.com/server_api"

        payload = json.dumps({
            "format": audio_format,
            "rate": rate,
            "channel": channel,
            "cuid": "qYi9Jv83W9SvZCxUSjFbXmFyBY5cvdnI",
            "token": get_access_token(API_KEY, SECRET_KEY),
            "speech": file_to_base64(filename),
            "len": get_file_size(filename)
        })
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload.encode("utf-8"))
        res = json.loads(response.text)
        if res.get("err_no") == 0:
            return res.get("result")[0]
        else:
            print(response.text)
            raise "error"

    @classmethod
    def get_answer(cls, text):
        url = "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/completions?access_token=" + get_access_token(
            API_KEY_chat, SECRET_KEY_chat)

        payload = json.dumps({
            "messages": [
                {
                    "role": "user",
                    "content": f"{text}。请用最简短的话告诉我,除了标点符号之外的字符也用文字表述。"
                }
            ],
            "temperature": 0.95,
            "top_p": 0.8,
            "penalty_score": 1,
            "enable_system_memory": False,
            "disable_search": False,
            "enable_citation": False,
            "response_format": "text"
        })
        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload.encode("utf-8"))
        res = json.loads(response.text)

        return res.get("result")
