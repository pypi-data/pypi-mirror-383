from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.market_basic_metadata_response import MarketBasicMetadataResponse


T = TypeVar("T", bound="MarketsResponse")


@_attrs_define
class MarketsResponse:
    """
    Attributes:
        total (float):
        limit (float):
        skip (float):
        results (list['MarketBasicMetadataResponse']):
    """

    total: float
    limit: float
    skip: float
    results: list["MarketBasicMetadataResponse"]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        total = self.total

        limit = self.limit

        skip = self.skip

        results = []
        for results_item_data in self.results:
            results_item = results_item_data.to_dict()
            results.append(results_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "total": total,
                "limit": limit,
                "skip": skip,
                "results": results,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.market_basic_metadata_response import MarketBasicMetadataResponse

        d = dict(src_dict)
        total = d.pop("total")

        limit = d.pop("limit")

        skip = d.pop("skip")

        results = []
        _results = d.pop("results")
        for results_item_data in _results:
            results_item = MarketBasicMetadataResponse.from_dict(results_item_data)

            results.append(results_item)

        markets_response = cls(
            total=total,
            limit=limit,
            skip=skip,
            results=results,
        )

        markets_response.additional_properties = d
        return markets_response

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
