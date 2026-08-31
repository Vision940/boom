from dataclasses import dataclass

from server.api.requests.base import ApiReq


class BoomBoardAvgReq(ApiReq): ...
class BoomBoardFreqReq(ApiReq): ...
class BoomBoardDroughtReq(ApiReq): ...


@dataclass
class BoomBoardTopReq(ApiReq):
    count: int

