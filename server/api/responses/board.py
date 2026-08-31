from server.api.responses.base import respdataclass, ApiResp


@respdataclass
class BoomBoardResp(ApiResp):
    board: dict

