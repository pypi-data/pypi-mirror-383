from __future__ import annotations

from typing import ClassVar, Dict

from conductor.client.codegen.models import Integration


class IntegrationAdapter(Integration):
    swagger_types: ClassVar[Dict[str, str]] = {
        "apis": "list[IntegrationApi]",
        "category": "str",
        "configuration": "dict(str, object)",
        "create_time": "int",
        "created_on": "int",
        "created_by": "str",
        "description": "str",
        "enabled": "bool",
        "models_count": "int",
        "name": "str",
        "owner_app": "str",
        "tags": "list[Tag]",
        "type": "str",
        "update_time": "int",
        "updated_on": "int",
        "updated_by": "str",
    }

    attribute_map: ClassVar[Dict[str, str]] = {
        "apis": "apis",
        "category": "category",
        "configuration": "configuration",
        "create_time": "createTime",
        "created_on": "createdOn",
        "created_by": "createdBy",
        "description": "description",
        "enabled": "enabled",
        "models_count": "modelsCount",
        "name": "name",
        "owner_app": "ownerApp",
        "tags": "tags",
        "type": "type",
        "update_time": "updateTime",
        "updated_on": "updatedOn",
        "updated_by": "updatedBy",
    }

    def __init__(
        self,
        apis=None,
        category=None,
        configuration=None,
        create_time=None,
        created_by=None,
        description=None,
        enabled=None,
        models_count=None,
        name=None,
        owner_app=None,
        tags=None,
        type=None,
        update_time=None,
        updated_by=None,
        updated_on=None,  # added to handle backwards compatibility
        created_on=None,  # added to handle backwards compatibility
    ):  # noqa: E501
        """Integration - a model defined in Swagger"""  # noqa: E501
        self._apis = None
        self._category = None
        self._configuration = None
        self._created_by = None
        self._description = None
        self._enabled = None
        self._models_count = None
        self._name = None
        self._owner_app = None
        self._tags = None
        self._type = None
        self._updated_by = None
        self.discriminator = None
        self._create_time = None
        self._update_time = None
        self._created_on = None
        self._updated_on = None

        if apis is not None:
            self.apis = apis
        if category is not None:
            self.category = category
        if configuration is not None:
            self.configuration = configuration
        if created_on is not None:
            self.create_time = created_on
            self.created_on = created_on
        if created_by is not None:
            self.created_by = created_by
        if description is not None:
            self.description = description
        if enabled is not None:
            self.enabled = enabled
        if models_count is not None:
            self.models_count = models_count
        if name is not None:
            self.name = name
        if owner_app is not None:
            self.owner_app = owner_app
        if tags is not None:
            self.tags = tags
        if type is not None:
            self.type = type
        if updated_by is not None:
            self.updated_by = updated_by
        if updated_on is not None:
            self.update_time = updated_on
            self.updated_on = updated_on

    @property
    def created_on(self):
        return self._create_time

    @created_on.setter
    def created_on(self, create_time):
        self._create_time = create_time
        self._created_on = create_time

    @property
    def updated_on(self):
        return self._update_time

    @updated_on.setter
    def updated_on(self, update_time):
        self._update_time = update_time
        self._updated_on = update_time

    @Integration.category.setter
    def category(self, category):
        allowed_values = [
            "API",
            "AI_MODEL",
            "VECTOR_DB",
            "RELATIONAL_DB",
            "MESSAGE_BROKER",
            "GIT",
            "EMAIL",
            "MCP",
            "CLOUD",
        ]  # noqa: E501
        if category not in allowed_values:
            raise ValueError(
                "Invalid value for `category` ({0}), must be one of {1}".format(  # noqa: E501
                    category, allowed_values
                )
            )

        self._category = category
