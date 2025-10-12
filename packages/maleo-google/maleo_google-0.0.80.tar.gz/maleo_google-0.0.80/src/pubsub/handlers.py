from pydantic import BaseModel, ConfigDict, Field
from typing import Generic
from .config.subscription import SubscriptionConfig
from .types import R, MessageController


class SubscriptionHandler(BaseModel, Generic[R]):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    config: SubscriptionConfig = Field(..., description="Subscription config")
    controller: MessageController[R] = Field(
        ..., description="Optional message controller"
    )


class SubscriptionHandlers(BaseModel):
    pass
