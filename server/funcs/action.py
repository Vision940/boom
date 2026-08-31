from __future__ import annotations

from dataclasses import asdict

from server import db
from static.games.boom.server.objs.action import (
    BoomRankAction
)


def parse_action_file(action_path, user_id) -> list[BoomAction]:
    actions = []

    with action_path.open() as action_file:
        for line_num, line in enumerate(action_file, start=1):
            line = line.strip()
            if not line: continue

            try:
                parts = line.split(maxsplit=3)
                if len(parts) < 3:
                    raise ValueError("Malformed action")

                action_type = parts[2]
                if action_type == "RANK":
                    actions.append(BoomRankAction.from_line(line, user_id))
                elif action_type in ["BOOMLOG", "CHATLOG"]:
                    #TODO: Handle these actions
                    # This should link into server log/chat room concept
                    continue
                else:
                    raise ValueError(f"Unsupported action '{action_type}'")
            except ValueError as e:
                raise ValueError(f"{e} on line {line_num}") from e

    return actions


def insert_actions(actions: list[BoomAction]):
    """
    Insert BoomAction objects into database from input array
    Returns (inserted, duplicate) line counts
    """

    inserted = 0
    duplicate = 0

    with db.db_cursor() as cursor:
        for action in actions:
            match action:
                case BoomRankAction():
                    was_inserted = _insert_rank_action(action, cursor)
                case _:
                    raise ValueError(f"Unsupported BOOM action type: {action.action}")

            if was_inserted:
                inserted += 1
            else:
                duplicate += 1

    return inserted, duplicate


def _insert_rank_action(action: BoomRankAction, cursor):
    """
    Insert RANK action into boom_command_rankings table in database
    returns True if new line added, False if duplicate
    raises ValueError on extremely unlikely uuid mismatch
    """

    row = db.fetch_row(
        """
        INSERT INTO boom_command_rankings (
            user_id,
            action_id,
            command,
            ranking,
            multiplier,
            odds,
            drought,
            host,
            is_import,
            is_quest,
            boomed_at
        )
        VALUES (
            %(user_id)s,
            %(action_id)s,
            %(command)s,
            %(ranking)s,
            %(multiplier)s,
            %(odds)s,
            %(drought)s,
            %(host)s,
            %(is_import)s,
            %(is_quest)s,
            to_timestamp(%(boomed_at)s)
        )
        ON CONFLICT (action_id) DO NOTHING
        RETURNING id
        """,
        {
            **asdict(action),
            "boomed_at": action.epoch_seconds
        },
        cursor=cursor
    )

    # Insert succeeded, new line added
    if row: return True

    # We have a UUID conflict
    existing = db.fetch_row(
        """
        SELECT
            EXTRACT(EPOCH FROM boomed_at)::BIGINT AS boomed_at
        FROM boom_command_rankings
        WHERE action_id = %(action_id)s
        """,
        {
            "action_id": action.action_id,
        },
        cursor=cursor
    )

    # This is a duplicate
    if existing and existing["boomed_at"] == action.epoch_seconds:
        return False

    # UUID collision - lucky?
    # If this ever does happen, need to regenerate uuid for action and re-sync
    raise ValueError(f"Action ID conflict: {action.action_id}")

