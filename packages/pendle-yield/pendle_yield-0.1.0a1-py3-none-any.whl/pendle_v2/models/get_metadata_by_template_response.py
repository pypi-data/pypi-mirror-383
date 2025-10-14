from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.get_metadata_by_template_response_values_item import GetMetadataByTemplateResponseValuesItem


T = TypeVar("T", bound="GetMetadataByTemplateResponse")


@_attrs_define
class GetMetadataByTemplateResponse:
    """
    Attributes:
        keys (list[str]):
        values (list['GetMetadataByTemplateResponseValuesItem']): Values of given metadata keys in the same order with
            keys
    """

    keys: list[str]
    values: list["GetMetadataByTemplateResponseValuesItem"]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        keys = self.keys

        values = []
        for values_item_data in self.values:
            values_item = values_item_data.to_dict()
            values.append(values_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "keys": keys,
                "values": values,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.get_metadata_by_template_response_values_item import GetMetadataByTemplateResponseValuesItem

        d = dict(src_dict)
        keys = cast(list[str], d.pop("keys"))

        values = []
        _values = d.pop("values")
        for values_item_data in _values:
            values_item = GetMetadataByTemplateResponseValuesItem.from_dict(values_item_data)

            values.append(values_item)

        get_metadata_by_template_response = cls(
            keys=keys,
            values=values,
        )

        get_metadata_by_template_response.additional_properties = d
        return get_metadata_by_template_response

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
