# coding: utf-8



from __future__ import annotations
import pprint
import re  # noqa: F401
import json

from pydantic import BaseModel, ConfigDict, Field, StrictStr, field_validator
from typing import Any, ClassVar, Dict, List, Optional
from typing_extensions import Annotated
from typing import Optional, Set
from typing_extensions import Self

class WorkspaceUpdate(BaseModel):
    """
    WorkspaceUpdate
    """ # noqa: E501
    display_name: Optional[Annotated[str, Field(min_length=3, strict=True, max_length=128)]] = Field(default=None, description="The display name of the workspace. It can be between 3 and 128 characters in length.", alias="displayName")
    mfa_types: Optional[List[StrictStr]] = Field(default=None, description="MFA types enabled for this workspace.", alias="mfaTypes")
    enabled_connections: Optional[List[StrictStr]] = Field(default=None, description="Enabled connections to login to the workspace. Null means no update.", alias="enabledConnections")
    __properties: ClassVar[List[str]] = ["displayName", "mfaTypes", "enabledConnections"]

    @field_validator('mfa_types')
    def mfa_types_validate_enum(cls, value):
        """Validates the enum"""
        if value is None:
            return value

        for i in value:
            if i not in set(['all']):
                raise ValueError("each list item must be one of ('all')")
        return value

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
        """Create an instance of WorkspaceUpdate from a JSON string"""
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
        # set to None if enabled_connections (nullable) is None
        # and model_fields_set contains the field
        if self.enabled_connections is None and "enabled_connections" in self.model_fields_set:
            _dict['enabledConnections'] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of WorkspaceUpdate from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "displayName": obj.get("displayName"),
            "mfaTypes": obj.get("mfaTypes"),
            "enabledConnections": obj.get("enabledConnections")
        })
        return _obj


