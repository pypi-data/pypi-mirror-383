# coding: utf-8



from __future__ import annotations
import pprint
import re  # noqa: F401
import json

from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictStr
from typing import Any, ClassVar, Dict, List, Optional
from tachyon_platform.models.user_role_input import UserRoleInput
from typing import Optional, Set
from typing_extensions import Self

class UserInvitationCreate(BaseModel):
    """
    UserInvitationCreate
    """ # noqa: E501
    invitee_email_address: StrictStr = Field(description="Email address of the user to invite.", alias="inviteeEmailAddress")
    roles: List[UserRoleInput] = Field(description="List of roles to assign to the invited user. If no roles are specified, the user will be invited as a member without any roles.")
    send_invitation_email: Optional[StrictBool] = Field(default=True, description="If true, Auth0 sends the invitation email to the invited user.", alias="sendInvitationEmail")
    __properties: ClassVar[List[str]] = ["inviteeEmailAddress", "roles", "sendInvitationEmail"]

    model_config = ConfigDict(
        populate_by_name=True,
        validate_assignment=True,
        protected_namespaces=(),
    )


    def to_str(self) -> str:
        """Returns the string representation of the model using alias"""
        return pprint.pformat(self.model_dump(by_alias=True))

    def to_json(self) -> str:
        """Returns the JSON representation of the model using alias"""
        # TODO: pydantic v2: use .model_dump_json(by_alias=True, exclude_unset=True) instead
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_str: str) -> Optional[Self]:
        """Create an instance of UserInvitationCreate from a JSON string"""
        return cls.from_dict(json.loads(json_str))

    def to_dict(self) -> Dict[str, Any]:
        """Return the dictionary representation of the model using alias.

        This has the following differences from calling pydantic's
        `self.model_dump(by_alias=True)`:

        * `None` is only added to the output dict for nullable fields that
          were set at model initialization. Other fields with value `None`
          are ignored.
        """
        excluded_fields: Set[str] = set([
        ])

        _dict = self.model_dump(
            by_alias=True,
            exclude=excluded_fields,
            exclude_none=True,
        )
        # override the default output from pydantic by calling `to_dict()` of each item in roles (list)
        _items = []
        if self.roles:
            for _item_roles in self.roles:
                if _item_roles:
                    _items.append(_item_roles.to_dict())
            _dict['roles'] = _items
        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of UserInvitationCreate from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "inviteeEmailAddress": obj.get("inviteeEmailAddress"),
            "roles": [UserRoleInput.from_dict(_item) for _item in obj["roles"]] if obj.get("roles") is not None else None,
            "sendInvitationEmail": obj.get("sendInvitationEmail") if obj.get("sendInvitationEmail") is not None else True
        })
        return _obj


