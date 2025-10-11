from __future__ import annotations

from typing import Any, Dict, Optional

from conductor.asyncio_client.http.models import UpdateWorkflowVariables


class UpdateWorkflowVariablesAdapter(UpdateWorkflowVariables):
    variables: Optional[Dict[str, Any]] = None
