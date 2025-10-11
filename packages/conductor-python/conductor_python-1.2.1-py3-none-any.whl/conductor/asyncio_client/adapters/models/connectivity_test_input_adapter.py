from __future__ import annotations

from typing import Any, Dict, Optional

from conductor.asyncio_client.http.models import ConnectivityTestInput


class ConnectivityTestInputAdapter(ConnectivityTestInput):
    input: Optional[Dict[str, Any]] = None
