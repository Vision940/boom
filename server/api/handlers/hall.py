from __future__ import annotations

from server import db
from server.games.context import GameContextProxy
from server.api.handlers.registry import handles

from static.games.boom.server.api.requests.hall import (
    BoomHallListReq
)
from static.games.boom.server.api.responses.hall import (
    BoomHallResp
)


BOOM_GAME = GameContextProxy(__name__)


@handles(BoomHallListReq)
def hall(req: BoomHallListReq) -> ApiResp:
    """
    Return BOOM hall of fame entries from boom_hall table
    """

    resp = BOOM_GAME.validate_api_req(req)
    if resp: return resp

    rows = db.fetch_rows(
        """
        SELECT
            u.username AS user,
            h.command,
            EXTRACT(EPOCH FROM h.boomed_at)::BIGINT AS boomed_at
        FROM boom_hall h
        JOIN users u
          ON u.id = h.user_id
        ORDER BY
            h.boomed_at ASC,
            h.id ASC
        """
    )

    return BoomHallResp(entries=rows)

