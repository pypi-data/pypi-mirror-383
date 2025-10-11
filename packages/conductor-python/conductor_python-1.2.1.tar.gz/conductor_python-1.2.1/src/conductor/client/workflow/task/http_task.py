from __future__ import annotations
from copy import deepcopy
from enum import Enum
from typing import Any, ClassVar, Dict, List, Optional, Union

from typing_extensions import Self

from conductor.client.workflow.task.task import TaskInterface
from conductor.client.workflow.task.task_type import TaskType


class HttpMethod(str, Enum):
    GET = "GET",
    PUT = "PUT",
    POST = "POST",
    DELETE = "DELETE",
    HEAD = "HEAD",
    OPTIONS = "OPTIONS"


class HttpInput:
    swagger_types: ClassVar[Dict[str, str]] = {
        "_uri": "str",
        "_method": "str",
        "_accept": "list[str]",
        "_headers": "dict[str, list[str]]",
        "_content_type": "str",
        "_connection_time_out": "int",
        "_read_timeout": "int",
        "_body": "str",
    }

    attribute_map: ClassVar[Dict[str, str]] = {
        "_uri": "uri",
        "_method": "method",
        "_accept": "accept",
        "_headers": "headers",
        "_content_type": "contentType",
        "_connection_time_out": "connectionTimeOut",
        "_read_timeout": "readTimeOut",
        "_body": "body",
    }

    def __init__(self,
                 method: HttpMethod = HttpMethod.GET,
                 uri: Optional[str] = None,
                 headers: Optional[Dict[str, List[str]]] = None,
                 accept: Optional[str] = None,
                 content_type: Optional[str] = None,
                 connection_time_out: Optional[int] = None,
                 read_timeout: Optional[int] = None,
                 body: Any = None) -> Self:
        self._method = deepcopy(method)
        self._uri = deepcopy(uri)
        self._headers = deepcopy(headers)
        self._accept = deepcopy(accept)
        self._content_type = deepcopy(content_type)
        self._connection_time_out = deepcopy(connection_time_out)
        self._read_timeout = deepcopy(read_timeout)
        self._body = deepcopy(body)


class HttpTask(TaskInterface):
    def __init__(self, task_ref_name: str, http_input: Union[HttpInput, dict]) -> Self:
        if type(http_input) is dict and "method" not in http_input:
            http_input["method"] = "GET"
        super().__init__(
            task_reference_name=task_ref_name,
            task_type=TaskType.HTTP,
            input_parameters={"http_request": http_input}
        )

    def status_code(self) -> int:
        return "${" + f"{self.task_reference_name}.output.response.statusCode" + "}"

    def headers(self, json_path: Optional[str] = None) -> str:
        if json_path is None:
            return "${" + f"{self.task_reference_name}.output.response.headers" + "}"
        else:
            return "${" + f"{self.task_reference_name}.output.response.headers.{json_path}" + "}"

    def body(self, json_path: Optional[str] = None) -> str:
        if json_path is None:
            return "${" + f"{self.task_reference_name}.output.response.body" + "}"
        else:
            return "${" + f"{self.task_reference_name}.output.response.body.{json_path}" + "}"
