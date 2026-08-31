from __future__ import annotations

from server import db
from server.funcs.user import user_id_from_username
from server.games.context import GameContextProxy
from server.api.handlers.registry import handles
from server.api.responses.base import ApiResp

from static.games.boom.server.api.requests.drought import (
    BoomDroughtLongestReq,
    BoomDroughtSyncReq
)
from static.games.boom.server.api.responses.drought import (
    BoomDroughtLongestResp
)


BOOM_GAME = GameContextProxy(__name__)


@handles(BoomDroughtSyncReq)
def sync(req: BoomDroughtSyncReq) -> ApiResp:
    """
    Update the boom_current_droughts table with the latest drought from the user
    Gets called in __boommeter and kicked off into the background
    """

    resp = BOOM_GAME.validate_api_req(req)
    if resp: return resp

    user_id = user_id_from_username(req.user)
    db.execute(
        """
        INSERT INTO boom_current_droughts (
            user_id,
            drought,
            observed_at
        )
        VALUES (
            %(user_id)s,
            %(drought)s,
            to_timestamp(%(epoch_seconds)s)
        )
        ON CONFLICT (user_id)
        DO UPDATE SET
            drought = EXCLUDED.drought,
            observed_at = EXCLUDED.observed_at,
            updated_at = NOW()
        WHERE
            EXCLUDED.observed_at >= boom_current_droughts.observed_at
        """,
        {
            "user_id": user_id,
            "drought": req.drought,
            "epoch_seconds": req.epochSeconds
        }
    )

    return ApiResp()


@handles(BoomDroughtLongestReq)
def longest(req: BoomDroughtLongestReq) -> ApiResp:
    """
    Returns longest current drought from boom_current_droughts table
    """

    resp = BOOM_GAME.validate_api_req(req)
    if resp: return resp

    row = db.fetch_row(
        """
        SELECT
            u.username AS user,
            d.drought AS longest
        FROM boom_current_droughts d
        JOIN users u
          ON u.id = d.user_id
        ORDER BY
            d.drought DESC,
            d.observed_at DESC
        LIMIT 1
        """
    )

    if not row:
        return BoomDroughtLongestResp(longest=0, user="nobody")
    return BoomDroughtLongestResp(longest=row["longest"], user=row["user"])

