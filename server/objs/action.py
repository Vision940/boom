from dataclasses import dataclass
from uuid import UUID

@dataclass
class BoomAction:
    action_id: UUID
    action: str
    epoch_seconds: int
    user_id: int
    

@dataclass
class BoomRankAction(BoomAction):
    command: str
    ranking: int
    multiplier: int
    odds: int
    host: str
    is_import: bool
    is_quest: bool
    drought: int | None = None

    @classmethod
    def from_line(cls, line, user_id) -> BoomRankAction:
        (
            action_id,
            epoch_seconds,
            action,
            command,
            ranking,
            multiplier,
            odds,
            host,
            is_import,
            is_quest,
            *rest,
        ) = line.split()

        if action != "RANK":
            raise ValueError(f"Initializing RANK action with action={action}")

        if len(rest) > 1:
            raise ValueError("Too many fields input to RANK action")

        return cls(
            action_id=UUID(action_id),
            action=action,
            epoch_seconds=int(epoch_seconds),
            user_id=int(user_id),
            command=command,
            ranking=int(ranking),
            multiplier=int(multiplier),
            odds=int(odds),
            host=host,
            is_import=is_import == "TRUE",
            is_quest=is_quest == "TRUE",
            drought=int(rest[0]) if rest else None,
        )

