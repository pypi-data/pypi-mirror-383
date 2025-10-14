from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="MarketImpliedApyDataPoint")


@_attrs_define
class MarketImpliedApyDataPoint:
    """
    Attributes:
        timestamp (float):
        implied_apy (float):
    """

    timestamp: float
    implied_apy: float
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        timestamp = self.timestamp

        implied_apy = self.implied_apy

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "timestamp": timestamp,
                "impliedApy": implied_apy,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        timestamp = d.pop("timestamp")

        implied_apy = d.pop("impliedApy")

        market_implied_apy_data_point = cls(
            timestamp=timestamp,
            implied_apy=implied_apy,
        )

        market_implied_apy_data_point.additional_properties = d
        return market_implied_apy_data_point

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
