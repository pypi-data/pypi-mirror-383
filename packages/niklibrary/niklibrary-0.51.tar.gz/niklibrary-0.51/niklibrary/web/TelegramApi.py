import time
import requests


class TelegramApi:

    def __init__(self, token, chat_id=None, message_thread_id=None):
        self.token = token
        self.base = "https://api.telegram.org"
        self.chat_id = chat_id
        self.message_thread_id = message_thread_id
        self.message_id = None
        self.msg = None
        self.last_msg = None
        self.urls = {}
        self.changelog = None

    def message(self, text, chat_id=None, replace_last_message=False, escape_text=True, parse_mode="markdown",
                ur_link=None, send_as_new_message=False):
        if self.token is None:
            return None
        if chat_id is None:
            chat_id = self.chat_id
        if text is None or str(text).__eq__(""):
            print("No text to send")
            return None
        if send_as_new_message:
            self.reset_message()
        if escape_text:
            for i in '_*[]~`>+=|{}':
                text = text.replace(i, "\\" + i)
        sending_text = text
        if self.message_id is not None:
            sending_text = self.msg.replace(self.last_msg, text) if replace_last_message else (self.msg + "\n" + text)
        data = {
            "chat_id": chat_id,
            "text": f"{sending_text}",
            "parse_mode": f"{parse_mode}",
            "disable_web_page_preview": True
        }
        if self.message_thread_id is not None:
            data["message_thread_id"] = self.message_thread_id
        url = f"{self.base}/bot{self.token}/sendMessage"
        if self.message_id is not None:
            data["message_id"] = self.message_id
            url = f"{self.base}/bot{self.token}/editMessageText"
        if ur_link is not None:
            ur_link: dict
            for key in ur_link:
                self.urls[key] = ur_link[key]
        if len(self.urls) > 0:
            row_list = []
            inline_list = []
            max_col = 1 if len(self.urls) > 1 else len(self.urls)
            for count, key in enumerate(self.urls):
                inline_list.append({"text": key, "url": self.urls[key]})
                if count == max_col:
                    row_list.append(inline_list)
                    inline_list = []
            if len(inline_list) > 0:
                row_list.append(inline_list)
            data["reply_markup"] = {
                "inline_keyboard": [
                    row for row in row_list
                ]
            }
        r = requests.post(url, json=data)
        response = r.json()
        if r.status_code != 200:
            print(f"Error sending message: {response}")
            if r.status_code == 429:
                print(f"Sleeping for {response['parameters']['retry_after']} seconds")
                time.sleep(response['parameters']['retry_after'])
            else:
                return None
        if response["ok"]:
            self.last_msg = text
            self.msg = sending_text
            self.message_id = response["result"]["message_id"]
        return response

    def delete_message(self, message_id=None, chat_id=None):
        if self.token is None:
            return None
        if chat_id is None:
            chat_id = self.chat_id
        if message_id is None:
            message_id = self.message_id
        if message_id is None:
            return None
        url = f"{self.base}/bot{self.token}/deleteMessage" \
              f"?chat_id={chat_id}" \
              f"&message_id={str(message_id)}"
        r = requests.get(url)
        response = r.json()
        return response

    def reset_message(self):
        self.message_id = None
        self.msg = None
        self.urls = {}
