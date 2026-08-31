from __future__ import annotations

from flask import request

from server.funcs import file as file_funcs
from server.funcs.user import user_id_from_username
from server.games.context import GameContextProxy
from server.api.handlers.registry import handles
from server.api.responses.base import ErrorResp

from static.games.boom.server.funcs import action as action_funcs
from static.games.boom.server.api.requests.action import (
    BoomActionSyncReq
)
from static.games.boom.server.api.responses.action import (
    BoomActionSyncResp
)


BOOM_GAME = GameContextProxy(__name__)


@handles(BoomActionSyncReq)
def sync(req: BoomActionSyncReq) -> ApiResp:
    resp = BOOM_GAME.validate_api_req(req)
    if resp: return resp

    file = request.files.get("file")
    result = file_funcs.save_upload(file, req.checksum, uuid_name=True)

    if isinstance(result, ErrorResp): return result
    action_path = result

    try:
        user_id = user_id_from_username(req.user)

        try:
            actions = action_funcs.parse_action_file(action_path, user_id)
        except (ValueError, UnicodeDecodeError) as e:
            return ErrorResp(error=str(e), errType="invalidactionfile", code=422)

        try:
            inserted, duplicate = action_funcs.insert_actions(actions)
        except ValueError as e:
            return ErrorResp(error=str(e), errType="failedactioninsert", code=422)

        return BoomActionSyncResp(inserted=inserted, duplicate=duplicate)
    finally:
        file_funcs.remove_file(action_path)

