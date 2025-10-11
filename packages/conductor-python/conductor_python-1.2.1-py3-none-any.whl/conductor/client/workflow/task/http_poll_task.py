from __future__ import annotations
from copy import deepcopy

from typing import Any, ClassVar, Dict, List, Optional

from typing_extensions import Self

from conductor.client.workflow.task.http_task import HttpMethod
from conductor.client.workflow.task.task import TaskInterface
from conductor.client.workflow.task.task_type import TaskType


class HttpPollInput():
    swagger_types: ClassVar[Dict[str, str]] = {
        "_uri": "str",
        "_method": "str",
        "_accept": "list[str]",
        "_headers": "dict[str, list[str]]",
        "_content_type": "str",
        "_connection_time_out": "int",
        "_read_timeout": "int",
        "_body": "str",
        "_termination_condition": "str",
        "_polling_interval": "int",
        "_max_poll_count": "int",
        "_polling_strategy": str
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
        "_termination_condition": "terminationCondition",
        "_polling_interval": "pollingInterval",
        "_max_poll_count": "maxPollCount",
        "_polling_strategy": "pollingStrategy"
    }

    def __init__(self,
                 termination_condition: Optional[str] = None,
                 max_poll_count : int = 100,
                 polling_interval : int = 100,
                 polling_strategy: str = "FIXED",
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
        self._termination_condition = termination_condition
        self._max_poll_count = max_poll_count
        self._polling_interval = polling_interval
        self._polling_strategy = polling_strategy


class HttpPollTask(TaskInterface):
    def __init__(self, task_ref_name: str, http_input: HttpPollInput) -> Self:
        super().__init__(
            task_reference_name=task_ref_name,
            task_type=TaskType.HTTP_POLL,
            input_parameters={"http_request": http_input}
        )
