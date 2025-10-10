from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="OnboardingCompanyValidationRequestRequest")


@_attrs_define
class OnboardingCompanyValidationRequestRequest:
    """
    Attributes:
        country (str): ISO country code (e.g., 'EE' for Estonia)
        legal_person_identifier (str): Official company registration code
        legal_name (Union[Unset, str]): Company name (optional, for reference)
        user_submitted_customer_metadata (Union[Unset, Any]): Optional customer metadata for manual verification cases.
            Should contain valid Customer model fields.
    """

    country: str
    legal_person_identifier: str
    legal_name: Union[Unset, str] = UNSET
    user_submitted_customer_metadata: Union[Unset, Any] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        country = self.country

        legal_person_identifier = self.legal_person_identifier

        legal_name = self.legal_name

        user_submitted_customer_metadata = self.user_submitted_customer_metadata

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "country": country,
                "legal_person_identifier": legal_person_identifier,
            }
        )
        if legal_name is not UNSET:
            field_dict["legal_name"] = legal_name
        if user_submitted_customer_metadata is not UNSET:
            field_dict["user_submitted_customer_metadata"] = user_submitted_customer_metadata

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        country = d.pop("country")

        legal_person_identifier = d.pop("legal_person_identifier")

        legal_name = d.pop("legal_name", UNSET)

        user_submitted_customer_metadata = d.pop("user_submitted_customer_metadata", UNSET)

        onboarding_company_validation_request_request = cls(
            country=country,
            legal_person_identifier=legal_person_identifier,
            legal_name=legal_name,
            user_submitted_customer_metadata=user_submitted_customer_metadata,
        )

        onboarding_company_validation_request_request.additional_properties = d
        return onboarding_company_validation_request_request

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
