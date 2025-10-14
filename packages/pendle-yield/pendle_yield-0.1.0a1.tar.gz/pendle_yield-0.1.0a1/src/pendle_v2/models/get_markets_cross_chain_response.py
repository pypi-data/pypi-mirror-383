from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.market_cross_chain_data import MarketCrossChainData


T = TypeVar("T", bound="GetMarketsCrossChainResponse")


@_attrs_define
class GetMarketsCrossChainResponse:
    """
    Attributes:
        markets (list['MarketCrossChainData']):
    """

    markets: list["MarketCrossChainData"]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        markets = []
        for markets_item_data in self.markets:
            markets_item = markets_item_data.to_dict()
            markets.append(markets_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "markets": markets,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.market_cross_chain_data import MarketCrossChainData

        d = dict(src_dict)
        markets = []
        _markets = d.pop("markets")
        for markets_item_data in _markets:
            markets_item = MarketCrossChainData.from_dict(markets_item_data)

            markets.append(markets_item)

        get_markets_cross_chain_response = cls(
            markets=markets,
        )

        get_markets_cross_chain_response.additional_properties = d
        return get_markets_cross_chain_response

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
