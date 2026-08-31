from __future__ import annotations

from server import db
from server.games.context import GameContextProxy
from server.api.handlers.registry import handles

from static.games.boom.server.api.requests.board import (
    BoomBoardAvgReq,
    BoomBoardFreqReq,
    BoomBoardDroughtReq,
    BoomBoardTopReq,
)
from static.games.boom.server.api.responses.board import (
    BoomBoardResp
)


BOOM_GAME = GameContextProxy(__name__)


def _command_board(rows):
    board = {}
    for row in rows:
        board.setdefault(row["user"], {})[row["command"]] = row["value"]
    return board


@handles(BoomBoardAvgReq)
def avg(req: BoomBoardAvgReq) -> ApiResp:
    resp = BOOM_GAME.validate_api_req(req)
    if resp: return resp

    rows = db.fetch_rows(
        """
        SELECT
            u.username AS user,
            s.command,
            s.avg_score AS value
        FROM boom_command_stats s
        JOIN users u
          ON u.id = s.user_id
        ORDER BY
            u.username,
            s.command
        """
    )

    return BoomBoardResp(board=_command_board(rows))


@handles(BoomBoardFreqReq)
def freq(req: BoomBoardFreqReq) -> ApiResp:
    resp = BOOM_GAME.validate_api_req(req)
    if resp: return resp

    rows = db.fetch_rows(
        """
        SELECT
            u.username AS user,
            s.command,
            s.entry_count AS value
        FROM boom_command_stats s
        JOIN users u
          ON u.id = s.user_id
        ORDER BY
            u.username,
            s.command
        """
    )

    return BoomBoardResp(board=_command_board(rows))


@handles(BoomBoardDroughtReq)
def drought(req: BoomBoardDroughtReq) -> ApiResp:
    resp = BOOM_GAME.validate_api_req(req)
    if resp: return resp

    rows = db.fetch_rows(
        """
        SELECT
            u.username AS user,
            COALESCE(h.drought, 0) AS longest,
            COALESCE(c.drought, 0) AS current
        FROM users u
        LEFT JOIN boom_highest_droughts h
          ON h.user_id = u.id
        LEFT JOIN boom_current_droughts c
          ON c.user_id = u.id
        WHERE
            h.user_id IS NOT NULL
            OR c.user_id IS NOT NULL
        ORDER BY u.username;
        """
    )

    board = {
        row["user"]: {
            "longest": row["longest"],
            "current": row["current"]
        } for row in rows
    }

    return BoomBoardResp(board=board)


@handles(BoomBoardTopReq)
def top(req: BoomBoardTopReq) -> ApiResp:
    resp = BOOM_GAME.validate_api_req(req)
    if resp: return resp

    rows = db.fetch_rows(
        """
        WITH ranked AS (
            SELECT
                s.user_id,
                s.command,
                s.entry_count,
                ROW_NUMBER() OVER (
                    PARTITION BY s.user_id
                    ORDER BY
                        s.entry_count DESC,
                        s.command ASC
                ) AS place
            FROM boom_command_stats s
        )
        SELECT
            u.username AS user,
            r.place,
            r.command,
            r.entry_count AS count
        FROM ranked r
        JOIN users u
          ON u.id = r.user_id
        WHERE r.place <= %(count)s
        ORDER BY
            u.username,
            r.place;
        """,
        {
            "count": req.count
        }
    )

    board = {}
    for row in rows:
        board.setdefault(row["user"], {})[str(row["place"])] = f"{row['command']} {row['count']}"

    return BoomBoardResp(board=board)

