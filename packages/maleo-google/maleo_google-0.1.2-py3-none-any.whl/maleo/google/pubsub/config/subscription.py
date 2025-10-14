from pydantic import BaseModel, Field
from typing import Annotated, Generic, Optional, TypeVar


class SubscriptionConfig(BaseModel):
    id: Annotated[str, Field(..., description="Subscription's ID")]
    max_messages: Annotated[
        int, Field(10, description="Subscription's Max messages")
    ] = 10
    ack_deadline: Annotated[
        int, Field(10, description="Subscription's ACK deadline")
    ] = 10


SubscriptionConfigT = TypeVar("SubscriptionConfigT", bound=SubscriptionConfig)


class SubscriptionsConfig(BaseModel):
    pass


SubscriptionsConfigT = TypeVar(
    "SubscriptionsConfigT", bound=Optional[SubscriptionsConfig]
)


class SubscriptionsConfigMixin(BaseModel, Generic[SubscriptionsConfigT]):
    subscriptions: SubscriptionsConfigT = Field(..., description="Subscriptions config")
