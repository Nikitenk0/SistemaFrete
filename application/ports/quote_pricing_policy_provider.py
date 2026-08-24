from datetime import datetime
from typing import Protocol

from domain.models.quote_pricing_policy import (
    QuotePricingPolicy
)


class QuotePricingPolicyProvider(Protocol):

    def get_effective_policy(
        self,
        at: datetime
    ) -> QuotePricingPolicy:
        ...