import requests


class HU:
    @staticmethod
    def get_html_content(url: str = "http://www.baidu.com") -> str:
        resp = requests.get(url)
        return resp.text
