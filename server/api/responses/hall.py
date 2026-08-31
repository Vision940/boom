from server.api.responses.base import respdataclass, ApiResp


@respdataclass
class BoomHallResp(ApiResp):
    entries: dict

