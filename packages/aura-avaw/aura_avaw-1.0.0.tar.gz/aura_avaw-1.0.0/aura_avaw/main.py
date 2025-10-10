import requests

class Main:
    def __init__(self, key1: str, key2: str):
        self.key1 = key1
        self.key2 = key2
        self.base_url = "https://aura.avaw.ir/a"

    def send_message(self, text: str, chat_token: str = "new") -> str | bool:
        url = f"{self.base_url}/{self.key1}/{self.key2}/sendMessage"
        data = {
            "chat_token": chat_token,
            "text": text
        }

        try:
            response = requests.post(url, data=data, timeout=10)
            if response.status_code >= 200 and response.status_code < 300:
                return response.text
        except requests.RequestException:
            return False

        return False

    def send_message_photo(self, text: str, url_photo: str, chat_token: str = "new") -> str | bool:
        url = f"{self.base_url}/{self.key1}/{self.key2}/sendMessage"
        data = {
            "chat_token": chat_token,
            "text": text,
            "photo": url_photo
        }

        try:
            response = requests.post(url, data=data, timeout=10)
            if response.status_code >= 200 and response.status_code < 300:
                return response.text
        except requests.RequestException:
            return False

        return False
