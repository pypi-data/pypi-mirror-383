from dataclasses import dataclass
from ..model import DataModel

@dataclass
class InteractionCallbackDataModel(DataModel):
    id: int
    """ID of the interaction."""

    type: int
    """Type of interaction."""

    activity_instance_id: str
    """Instance ID of activity if an activity was launched or joined."""

    response_message_id: int
    """ID of the message created by the interaction."""

    response_message_loading: bool
    """If the interaction is in a loading state."""

    response_message_ephemeral: bool
    """If the interaction is ephemeral."""

@dataclass
class InteractionCallbackModel(DataModel):
    interaction: InteractionCallbackDataModel
