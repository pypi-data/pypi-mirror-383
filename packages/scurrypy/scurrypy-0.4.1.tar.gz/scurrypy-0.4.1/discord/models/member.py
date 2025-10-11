from dataclasses import dataclass
from ..model import DataModel
from ..models.user import UserModel

@dataclass
class MemberModel(DataModel):
    """Represents a guild member."""

    roles: list[int]
    """List of roles registered to the guild member."""

    user: UserModel
    """User data associated with the guild member."""

    nick: str
    """Server nickname of the guild member."""

    avatar: str
    """Server avatar hash of the guild mmeber."""

    joined_at: str
    """ISO8601 timestamp of when the guild member joined server."""
    deaf: bool
    """If the member is deaf in a VC (input)."""

    mute: bool
    """If the member is muted in VC (output)."""
