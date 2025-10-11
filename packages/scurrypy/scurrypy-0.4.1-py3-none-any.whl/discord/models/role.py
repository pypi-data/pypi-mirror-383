from dataclasses import dataclass
from typing import Optional
from ..model import DataModel

@dataclass
class RoleColors(DataModel):
    """Role color data."""

    primary_color: int
    """Primary color of the role."""

    secondary_color: int
    """Secondary color of the role. Creates a gradient."""

    tertiary_color: int
    """Tertiary color of the role. Creates a holographic style."""

@dataclass
class RoleModel(DataModel):
    """Represents a Discord role."""

    id: int
    """ID of the role."""

    name: str
    """Name of the role."""

    colors: RoleColors
    """Colors of the role."""

    hoist: bool
    """If the role is pinned in user listing."""

    position: int
    """Position of the role."""

    permissions: str
    """Permission bit set."""

    managed: bool
    """If the role is managed by an integration."""

    mentionable: bool
    """If the role is mentionable."""

    flags: int
    """Role flags combined as a bitfield."""

    icon: Optional[str] = None
    """Icon hash of the role."""

    unicode_emoji: Optional[str] = None
    """Unicode emoji of the role."""
