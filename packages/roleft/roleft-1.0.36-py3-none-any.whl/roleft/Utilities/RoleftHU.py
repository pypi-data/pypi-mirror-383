import requests


class HU:

    @staticmethod
    def GetHtmlContent(url: str = "http://www.baidu.com") -> str:
        resp = requests.get(url)
        return resp.text
