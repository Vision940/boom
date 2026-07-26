from server.api.auth import validate_api_req
from server.api.handlers.registry import handles
from server.games.context import GameContextProxy

from static.games.boom.server.api.requests.action import (
    ActionRankReq
)
from static.games.boom.server.api.responses.action import (
    BoomActionResp
)


BOOM_GAME = GameContextProxy(__name__)


@handles(ActionRankReq)
def rank(req: ActionRankReq) -> ApiResp:
    resp = BOOM_GAME.validate_api_req(req)
    if resp: return resp

    return BoomActionResp()

