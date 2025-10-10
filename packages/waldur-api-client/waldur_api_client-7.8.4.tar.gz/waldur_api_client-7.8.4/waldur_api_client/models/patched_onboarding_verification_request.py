import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="PatchedOnboardingVerificationRequest")


@_attrs_define
class PatchedOnboardingVerificationRequest:
    """
    Attributes:
        user (Union[Unset, int]): User requesting company onboarding
        country (Union[Unset, str]): ISO country code (e.g., 'EE' for Estonia)
        legal_person_identifier (Union[Unset, str]): Official company registration code
        legal_name (Union[Unset, str]): Claimed company name (optional, for reference)
        user_submitted_customer_metadata (Union[Unset, Any]): Additional customer metadata submitted by user for manual
            verification cases. Should contain valid Customer model fields.
        expires_at (Union[None, Unset, datetime.datetime]): When this verification expires
    """

    user: Union[Unset, int] = UNSET
    country: Union[Unset, str] = UNSET
    legal_person_identifier: Union[Unset, str] = UNSET
    legal_name: Union[Unset, str] = UNSET
    user_submitted_customer_metadata: Union[Unset, Any] = UNSET
    expires_at: Union[None, Unset, datetime.datetime] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        user = self.user

        country = self.country

        legal_person_identifier = self.legal_person_identifier

        legal_name = self.legal_name

        user_submitted_customer_metadata = self.user_submitted_customer_metadata

        expires_at: Union[None, Unset, str]
        if isinstance(self.expires_at, Unset):
            expires_at = UNSET
        elif isinstance(self.expires_at, datetime.datetime):
            expires_at = self.expires_at.isoformat()
        else:
            expires_at = self.expires_at

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if user is not UNSET:
            field_dict["user"] = user
        if country is not UNSET:
            field_dict["country"] = country
        if legal_person_identifier is not UNSET:
            field_dict["legal_person_identifier"] = legal_person_identifier
        if legal_name is not UNSET:
            field_dict["legal_name"] = legal_name
        if user_submitted_customer_metadata is not UNSET:
            field_dict["user_submitted_customer_metadata"] = user_submitted_customer_metadata
        if expires_at is not UNSET:
            field_dict["expires_at"] = expires_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        user = d.pop("user", UNSET)

        country = d.pop("country", UNSET)

        legal_person_identifier = d.pop("legal_person_identifier", UNSET)

        legal_name = d.pop("legal_name", UNSET)

        user_submitted_customer_metadata = d.pop("user_submitted_customer_metadata", UNSET)

        def _parse_expires_at(data: object) -> Union[None, Unset, datetime.datetime]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                expires_at_type_0 = isoparse(data)

                return expires_at_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, datetime.datetime], data)

        expires_at = _parse_expires_at(d.pop("expires_at", UNSET))

        patched_onboarding_verification_request = cls(
            user=user,
            country=country,
            legal_person_identifier=legal_person_identifier,
            legal_name=legal_name,
            user_submitted_customer_metadata=user_submitted_customer_metadata,
            expires_at=expires_at,
        )

        patched_onboarding_verification_request.additional_properties = d
        return patched_onboarding_verification_request

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
