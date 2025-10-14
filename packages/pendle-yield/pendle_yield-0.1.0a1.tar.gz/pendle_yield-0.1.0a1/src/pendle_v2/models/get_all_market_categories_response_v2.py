from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.market_category_response import MarketCategoryResponse


T = TypeVar("T", bound="GetAllMarketCategoriesResponseV2")


@_attrs_define
class GetAllMarketCategoriesResponseV2:
    """
    Attributes:
        categories (list['MarketCategoryResponse']):
    """

    categories: list["MarketCategoryResponse"]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        categories = []
        for categories_item_data in self.categories:
            categories_item = categories_item_data.to_dict()
            categories.append(categories_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "categories": categories,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.market_category_response import MarketCategoryResponse

        d = dict(src_dict)
        categories = []
        _categories = d.pop("categories")
        for categories_item_data in _categories:
            categories_item = MarketCategoryResponse.from_dict(categories_item_data)

            categories.append(categories_item)

        get_all_market_categories_response_v2 = cls(
            categories=categories,
        )

        get_all_market_categories_response_v2.additional_properties = d
        return get_all_market_categories_response_v2

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
