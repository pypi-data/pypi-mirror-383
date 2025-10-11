from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import Field
from typing_extensions import Self

from conductor.asyncio_client.http.models import DescriptorProtoOrBuilder


class DescriptorProtoOrBuilderAdapter(DescriptorProtoOrBuilder):
    all_fields: Optional[Dict[str, Any]] = Field(default=None, alias="allFields")
    default_instance_for_type: Optional["MessageAdapter"] = Field(
        default=None, alias="defaultInstanceForType"
    )
    descriptor_for_type: Optional["DescriptorAdapter"] = Field(
        default=None, alias="descriptorForType"
    )
    enum_type_list: Optional[List["EnumDescriptorProtoAdapter"]] = Field(
        default=None, alias="enumTypeList"
    )
    enum_type_or_builder_list: Optional[List["EnumDescriptorProtoOrBuilderAdapter"]] = (
        Field(default=None, alias="enumTypeOrBuilderList")
    )
    extension_list: Optional[List["FieldDescriptorProtoAdapter"]] = Field(
        default=None, alias="extensionList"
    )
    extension_or_builder_list: Optional[
        List["FieldDescriptorProtoOrBuilderAdapter"]
    ] = Field(default=None, alias="extensionOrBuilderList")
    extension_range_list: Optional[List["ExtensionRangeAdapter"]] = Field(
        default=None, alias="extensionRangeList"
    )
    extension_range_or_builder_list: Optional[
        List["ExtensionRangeOrBuilderAdapter"]
    ] = Field(default=None, alias="extensionRangeOrBuilderList")
    field_list: Optional[List["FieldDescriptorProtoAdapter"]] = Field(
        default=None, alias="fieldList"
    )
    field_or_builder_list: Optional[List["FieldDescriptorProtoOrBuilderAdapter"]] = (
        Field(default=None, alias="fieldOrBuilderList")
    )
    nested_type_list: Optional[List["DescriptorProtoAdapter"]] = Field(
        default=None, alias="nestedTypeList"
    )
    oneof_decl_list: Optional[List["OneofDescriptorProtoAdapter"]] = Field(
        default=None, alias="oneofDeclList"
    )
    oneof_decl_or_builder_list: Optional[
        List["OneofDescriptorProtoOrBuilderAdapter"]
    ] = Field(default=None, alias="oneofDeclOrBuilderList")
    options_or_builder: Optional["MessageOptionsOrBuilderAdapter"] = Field(
        default=None, alias="optionsOrBuilder"
    )
    reserved_range_list: Optional[List["ReservedRangeAdapter"]] = Field(
        default=None, alias="reservedRangeList"
    )
    reserved_range_or_builder_list: Optional[List["ReservedRangeOrBuilderAdapter"]] = (
        Field(default=None, alias="reservedRangeOrBuilderList")
    )
    unknown_fields: Optional["UnknownFieldSetAdapter"] = Field(
        default=None, alias="unknownFields"
    )

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of DescriptorProtoOrBuilder from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate(
            {
                "allFields": obj.get("allFields"),
                "defaultInstanceForType": (
                    MessageAdapter.from_dict(obj["defaultInstanceForType"])
                    if obj.get("defaultInstanceForType") is not None
                    else None
                ),
                "descriptorForType": (
                    DescriptorAdapter.from_dict(obj["descriptorForType"])
                    if obj.get("descriptorForType") is not None
                    else None
                ),
                "enumTypeCount": obj.get("enumTypeCount"),
                "enumTypeList": (
                    [
                        EnumDescriptorProtoAdapter.from_dict(_item)
                        for _item in obj["enumTypeList"]
                    ]
                    if obj.get("enumTypeList") is not None
                    else None
                ),
                "enumTypeOrBuilderList": (
                    [
                        EnumDescriptorProtoOrBuilderAdapter.from_dict(_item)
                        for _item in obj["enumTypeOrBuilderList"]
                    ]
                    if obj.get("enumTypeOrBuilderList") is not None
                    else None
                ),
                "extensionCount": obj.get("extensionCount"),
                "extensionList": (
                    [
                        FieldDescriptorProtoAdapter.from_dict(_item)
                        for _item in obj["extensionList"]
                    ]
                    if obj.get("extensionList") is not None
                    else None
                ),
                "extensionOrBuilderList": (
                    [
                        FieldDescriptorProtoOrBuilderAdapter.from_dict(_item)
                        for _item in obj["extensionOrBuilderList"]
                    ]
                    if obj.get("extensionOrBuilderList") is not None
                    else None
                ),
                "extensionRangeCount": obj.get("extensionRangeCount"),
                "extensionRangeList": (
                    [
                        ExtensionRangeAdapter.from_dict(_item)
                        for _item in obj["extensionRangeList"]
                    ]
                    if obj.get("extensionRangeList") is not None
                    else None
                ),
                "extensionRangeOrBuilderList": (
                    [
                        ExtensionRangeOrBuilderAdapter.from_dict(_item)
                        for _item in obj["extensionRangeOrBuilderList"]
                    ]
                    if obj.get("extensionRangeOrBuilderList") is not None
                    else None
                ),
                "fieldCount": obj.get("fieldCount"),
                "fieldList": (
                    [
                        FieldDescriptorProtoAdapter.from_dict(_item)
                        for _item in obj["fieldList"]
                    ]
                    if obj.get("fieldList") is not None
                    else None
                ),
                "fieldOrBuilderList": (
                    [
                        FieldDescriptorProtoOrBuilderAdapter.from_dict(_item)
                        for _item in obj["fieldOrBuilderList"]
                    ]
                    if obj.get("fieldOrBuilderList") is not None
                    else None
                ),
                "initializationErrorString": obj.get("initializationErrorString"),
                "initialized": obj.get("initialized"),
                "name": obj.get("name"),
                "nameBytes": (
                    ByteStringAdapter.from_dict(obj["nameBytes"])
                    if obj.get("nameBytes") is not None
                    else None
                ),
                "nestedTypeCount": obj.get("nestedTypeCount"),
                "nestedTypeList": (
                    [
                        DescriptorProtoAdapter.from_dict(_item)
                        for _item in obj["nestedTypeList"]
                    ]
                    if obj.get("nestedTypeList") is not None
                    else None
                ),
                "oneofDeclCount": obj.get("oneofDeclCount"),
                "oneofDeclList": (
                    [
                        OneofDescriptorProtoAdapter.from_dict(_item)
                        for _item in obj["oneofDeclList"]
                    ]
                    if obj.get("oneofDeclList") is not None
                    else None
                ),
                "oneofDeclOrBuilderList": (
                    [
                        OneofDescriptorProtoOrBuilderAdapter.from_dict(_item)
                        for _item in obj["oneofDeclOrBuilderList"]
                    ]
                    if obj.get("oneofDeclOrBuilderList") is not None
                    else None
                ),
                "options": (
                    MessageOptionsAdapter.from_dict(obj["options"])
                    if obj.get("options") is not None
                    else None
                ),
                "optionsOrBuilder": (
                    MessageOptionsOrBuilderAdapter.from_dict(obj["optionsOrBuilder"])
                    if obj.get("optionsOrBuilder") is not None
                    else None
                ),
                "reservedNameCount": obj.get("reservedNameCount"),
                "reservedNameList": obj.get("reservedNameList"),
                "reservedRangeCount": obj.get("reservedRangeCount"),
                "reservedRangeList": (
                    [
                        ReservedRangeAdapter.from_dict(_item)
                        for _item in obj["reservedRangeList"]
                    ]
                    if obj.get("reservedRangeList") is not None
                    else None
                ),
                "reservedRangeOrBuilderList": (
                    [
                        ReservedRangeOrBuilderAdapter.from_dict(_item)
                        for _item in obj["reservedRangeOrBuilderList"]
                    ]
                    if obj.get("reservedRangeOrBuilderList") is not None
                    else None
                ),
                "unknownFields": (
                    UnknownFieldSetAdapter.from_dict(obj["unknownFields"])
                    if obj.get("unknownFields") is not None
                    else None
                ),
            }
        )
        return _obj


from conductor.asyncio_client.adapters.models.byte_string_adapter import (  # noqa: E402
    ByteStringAdapter,
)
from conductor.asyncio_client.adapters.models.descriptor_adapter import (  # noqa: E402
    DescriptorAdapter,
)
from conductor.asyncio_client.adapters.models.descriptor_proto_adapter import (  # noqa: E402
    DescriptorProtoAdapter,
)
from conductor.asyncio_client.adapters.models.enum_descriptor_proto_adapter import (  # noqa: E402
    EnumDescriptorProtoAdapter,
)
from conductor.asyncio_client.adapters.models.enum_descriptor_proto_or_builder_adapter import (  # noqa: E402
    EnumDescriptorProtoOrBuilderAdapter,
)
from conductor.asyncio_client.adapters.models.extension_range_adapter import (  # noqa: E402
    ExtensionRangeAdapter,
)
from conductor.asyncio_client.adapters.models.extension_range_or_builder_adapter import (  # noqa: E402
    ExtensionRangeOrBuilderAdapter,
)
from conductor.asyncio_client.adapters.models.field_descriptor_proto_adapter import (  # noqa: E402
    FieldDescriptorProtoAdapter,
)
from conductor.asyncio_client.adapters.models.field_descriptor_proto_or_builder_adapter import (  # noqa: E402
    FieldDescriptorProtoOrBuilderAdapter,
)
from conductor.asyncio_client.adapters.models.message_adapter import (  # noqa: E402
    MessageAdapter,
)
from conductor.asyncio_client.adapters.models.message_options_or_builder_adapter import (  # noqa: E402
    MessageOptionsOrBuilderAdapter,
)
from conductor.asyncio_client.adapters.models.oneof_descriptor_proto_adapter import (  # noqa: E402
    OneofDescriptorProtoAdapter,
)
from conductor.asyncio_client.adapters.models.oneof_descriptor_proto_or_builder_adapter import (  # noqa: E402
    OneofDescriptorProtoOrBuilderAdapter,
)
from conductor.asyncio_client.adapters.models.reserved_range_adapter import (  # noqa: E402
    ReservedRangeAdapter,
)
from conductor.asyncio_client.adapters.models.reserved_range_or_builder_adapter import (  # noqa: E402
    ReservedRangeOrBuilderAdapter,
)
from conductor.asyncio_client.adapters.models.unknown_field_set_adapter import (  # noqa: E402
    UnknownFieldSetAdapter,
)
from conductor.asyncio_client.adapters.models.message_options_adapter import (  # noqa: E402
    MessageOptionsAdapter,
)

DescriptorProtoOrBuilderAdapter.model_rebuild(raise_errors=False)
