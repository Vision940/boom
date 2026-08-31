from dataclasses import dataclass

from server.api.requests.base import ApiReq


@dataclass
class BoomActionSyncReq(ApiReq):
    checksum: str

