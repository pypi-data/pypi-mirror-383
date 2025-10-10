from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PatchedOnboardingJustificationRequest")


@_attrs_define
class PatchedOnboardingJustificationRequest:
    """
    Attributes:
        verification (Union[Unset, int]):
        user (Union[Unset, int]):
        user_justification (Union[Unset, str]): User's explanation for why they should be authorized
    """

    verification: Union[Unset, int] = UNSET
    user: Union[Unset, int] = UNSET
    user_justification: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        verification = self.verification

        user = self.user

        user_justification = self.user_justification

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if verification is not UNSET:
            field_dict["verification"] = verification
        if user is not UNSET:
            field_dict["user"] = user
        if user_justification is not UNSET:
            field_dict["user_justification"] = user_justification

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        verification = d.pop("verification", UNSET)

        user = d.pop("user", UNSET)

        user_justification = d.pop("user_justification", UNSET)

        patched_onboarding_justification_request = cls(
            verification=verification,
            user=user,
            user_justification=user_justification,
        )

        patched_onboarding_justification_request.additional_properties = d
        return patched_onboarding_justification_request

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
