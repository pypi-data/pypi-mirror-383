from abc import ABC, abstractmethod
from enum import Enum
import requests

# import json
from dataclasses import dataclass, fields
from typing import Optional, Type, TypeVar

from tests.test_9 import download_youtube_video


class ApiType(Enum):
    Unknown = 0
    TakeVideoTask = 1
    ReportVideoStatus = 2


@dataclass
class BaseParam(ABC):
    @property
    @abstractmethod
    def api_type(self) -> ApiType:
        pass

    @property
    @abstractmethod
    def json_obj(self) -> dict:
        pass


@dataclass
class BaseResult(ABC):
    errMsg: str | None = "123"
    succ: bool = False


@dataclass
class TakeVideoTaskParam(BaseParam):
    @property
    def api_type(self) -> ApiType:
        return ApiType.TakeVideoTask

    @property
    def json_obj(self) -> dict:
        return {}


class YtbVideoStatus(Enum):
    Unknown = 0
    Init = 1
    Done = 2
    Fail = 3


@dataclass
class ReportVideoStatusParam(BaseParam):
    browserUrl: str = ""
    status: YtbVideoStatus = YtbVideoStatus.Unknown

    @property
    def api_type(self) -> ApiType:
        return ApiType.ReportVideoStatus

    @property
    def json_obj(self) -> dict:
        return {"browserUrl": self.browserUrl, "status": self.status.name}


@dataclass
class TakeVideoTaskResult(BaseResult):
    browserUrl: str = ""
    need2Exatract: bool = False

    @classmethod
    def from_json(cls, data: dict) -> "TakeVideoTaskResult":
        init_args = {}
        for f in fields(cls):
            if f.name in data:
                init_args[f.name] = data[f.name]

        return cls(**init_args)


TParam = TypeVar("TParam", bound=BaseParam)
TResult = TypeVar("TResult", bound=BaseResult)


def call_restful_api(param: TParam) -> dict | None:
    url = f"https://www.suanqian.com/api/{param.api_type.name}"
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(url, json=param.json_obj, headers=headers)
        response.raise_for_status()
        result = response.json()
        return result.get("data", {})
    except requests.RequestException as e:
        print(f"Error calling API: {e}")
        return None


class SlaveHttpClient:
    @staticmethod
    def invoke(param: TParam, cls: Type[TResult]) -> TResult:
        data = call_restful_api(param)
        return cls.from_json(data) if data else cls()  # type: ignore


if __name__ == "__main__":
    result = SlaveHttpClient.invoke(TakeVideoTaskParam(), TakeVideoTaskResult)

    if result.need2Exatract:
        download_youtube_video(result.browserUrl)
    if result:
        print(f"Browser URL: {result.browserUrl}")
        print(f"Need to Extract: {result.need2Exatract}")
