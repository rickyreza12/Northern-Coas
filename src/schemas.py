from dataclasses import dataclass
from typing import Literal

LicenseStatus = Literal["unknown", "active", "pending", "inactive"]


@dataclass
class Facts:
    product: int = 0
    monthly_volume: float | None = None
    one_off_volume: float | None = None
    wholesale: bool = False
    personal: bool = False
    non_beverage: bool = False
    license: LicenseStatus = "unknown"
    business: bool = False
    years: int = 0
    accounts: int = 0
    volume_uncertain: bool = False
