from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.market_total_fees_data import MarketTotalFeesData


T = TypeVar("T", bound="AllMarketTotalFeesResponse")


@_attrs_define
class AllMarketTotalFeesResponse:
    """
    Attributes:
        results (list['MarketTotalFeesData']): all market total fees response
    """

    results: list["MarketTotalFeesData"]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        results = []
        for results_item_data in self.results:
            results_item = results_item_data.to_dict()
            results.append(results_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "results": results,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.market_total_fees_data import MarketTotalFeesData

        d = dict(src_dict)
        results = []
        _results = d.pop("results")
        for results_item_data in _results:
            results_item = MarketTotalFeesData.from_dict(results_item_data)

            results.append(results_item)

        all_market_total_fees_response = cls(
            results=results,
        )

        all_market_total_fees_response.additional_properties = d
        return all_market_total_fees_response

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
