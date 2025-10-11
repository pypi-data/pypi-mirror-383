from dataclasses import dataclass
from ..model import DataModel

from urllib.parse import quote

@dataclass
class EmojiModel(DataModel):
    """Represents a Discord emoji."""
    name: str
    """Name of emoji."""

    id: int = 0
    """ID of the emoji (if custom)."""

    animated: bool = False
    """If the emoji is animated. Defaults to `False`."""

    @property
    def mention(self) -> str:
        """For use in message content."""
        return f"<a:{self.name}:{self.id}>" if self.animated else f"<:{self.name}:{self.id}>"

    @property
    def api_code(self) -> str:
        """Return the correct API code for this emoji (URL-safe)."""
        if not self.id:
            # unicode emoji
            return quote(self.name)

        # custom emoji
        if self.animated:
            return quote(f"a:{self.name}:{self.id}")
        
        return quote(f"{self.name}:{self.id}")
