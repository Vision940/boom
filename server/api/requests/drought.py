from dataclasses import dataclass

from server.api.requests.base import ApiReq


@dataclass
class BoomDroughtSyncReq(ApiReq):
    drought: int
    epochSeconds: int


class BoomDroughtLongestReq(ApiReq): ...

