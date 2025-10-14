import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

if TYPE_CHECKING:
    from ..models.pool_v2_response import PoolV2Response
    from ..models.ve_pendle_data_response_month_airdrop_breakdown_item import (
        VePendleDataResponseMonthAirdropBreakdownItem,
    )


T = TypeVar("T", bound="VePendleDataResponse")


@_attrs_define
class VePendleDataResponse:
    """
    Attributes:
        avg_lock_duration (float): Average lock duration in days
        total_pendle_locked (float):
        ve_pendle_supply (float):
        month_total_swap_fee (float):
        airdrop_from_date (datetime.datetime):
        month_airdrop_breakdown (list['VePendleDataResponseMonthAirdropBreakdownItem']):
        total_projected_votes (float):
        total_current_votes (float):
        pools (list['PoolV2Response']):
    """

    avg_lock_duration: float
    total_pendle_locked: float
    ve_pendle_supply: float
    month_total_swap_fee: float
    airdrop_from_date: datetime.datetime
    month_airdrop_breakdown: list["VePendleDataResponseMonthAirdropBreakdownItem"]
    total_projected_votes: float
    total_current_votes: float
    pools: list["PoolV2Response"]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        avg_lock_duration = self.avg_lock_duration

        total_pendle_locked = self.total_pendle_locked

        ve_pendle_supply = self.ve_pendle_supply

        month_total_swap_fee = self.month_total_swap_fee

        airdrop_from_date = self.airdrop_from_date.isoformat()

        month_airdrop_breakdown = []
        for month_airdrop_breakdown_item_data in self.month_airdrop_breakdown:
            month_airdrop_breakdown_item = month_airdrop_breakdown_item_data.to_dict()
            month_airdrop_breakdown.append(month_airdrop_breakdown_item)

        total_projected_votes = self.total_projected_votes

        total_current_votes = self.total_current_votes

        pools = []
        for pools_item_data in self.pools:
            pools_item = pools_item_data.to_dict()
            pools.append(pools_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "avgLockDuration": avg_lock_duration,
                "totalPendleLocked": total_pendle_locked,
                "vePendleSupply": ve_pendle_supply,
                "monthTotalSwapFee": month_total_swap_fee,
                "airdropFromDate": airdrop_from_date,
                "monthAirdropBreakdown": month_airdrop_breakdown,
                "totalProjectedVotes": total_projected_votes,
                "totalCurrentVotes": total_current_votes,
                "pools": pools,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.pool_v2_response import PoolV2Response
        from ..models.ve_pendle_data_response_month_airdrop_breakdown_item import (
            VePendleDataResponseMonthAirdropBreakdownItem,
        )

        d = dict(src_dict)
        avg_lock_duration = d.pop("avgLockDuration")

        total_pendle_locked = d.pop("totalPendleLocked")

        ve_pendle_supply = d.pop("vePendleSupply")

        month_total_swap_fee = d.pop("monthTotalSwapFee")

        airdrop_from_date = isoparse(d.pop("airdropFromDate"))

        month_airdrop_breakdown = []
        _month_airdrop_breakdown = d.pop("monthAirdropBreakdown")
        for month_airdrop_breakdown_item_data in _month_airdrop_breakdown:
            month_airdrop_breakdown_item = VePendleDataResponseMonthAirdropBreakdownItem.from_dict(
                month_airdrop_breakdown_item_data
            )

            month_airdrop_breakdown.append(month_airdrop_breakdown_item)

        total_projected_votes = d.pop("totalProjectedVotes")

        total_current_votes = d.pop("totalCurrentVotes")

        pools = []
        _pools = d.pop("pools")
        for pools_item_data in _pools:
            pools_item = PoolV2Response.from_dict(pools_item_data)

            pools.append(pools_item)

        ve_pendle_data_response = cls(
            avg_lock_duration=avg_lock_duration,
            total_pendle_locked=total_pendle_locked,
            ve_pendle_supply=ve_pendle_supply,
            month_total_swap_fee=month_total_swap_fee,
            airdrop_from_date=airdrop_from_date,
            month_airdrop_breakdown=month_airdrop_breakdown,
            total_projected_votes=total_projected_votes,
            total_current_votes=total_current_votes,
            pools=pools,
        )

        ve_pendle_data_response.additional_properties = d
        return ve_pendle_data_response

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
