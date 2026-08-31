from server.api.responses.base import respdataclass, ApiResp


@respdataclass
class BoomDroughtLongestResp(ApiResp):
    longest: int
    user: str

