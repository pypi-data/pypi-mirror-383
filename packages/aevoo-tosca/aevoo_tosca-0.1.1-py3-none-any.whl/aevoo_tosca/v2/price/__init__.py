from aevoo_tosca.v2.common.default_base_model import DefaultBaseModel


class Price(DefaultBaseModel):
    item_prices: dict[str, float] | None = None
    unit_price: float | None = None


class InputMargin(DefaultBaseModel):
    add: int = 0
    margin: float = 1
    quantity_of: str | None = None


class Prices(DefaultBaseModel):
    per_hour: Price | None = None
    per_month: Price | None = None


class ServicePrice(DefaultBaseModel):
    inputs: dict[str, InputMargin] = None
    per_hour: float | None = None
    per_month: float | None = None
