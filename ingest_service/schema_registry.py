import json
import hashlib
import logging
import os
from typing import Type
from urllib import request

from pydantic import BaseModel

logger = logging.getLogger(__name__)


def register_schema(model: Type[BaseModel], subject: str) -> str:
    """Register *model* with Karapace and return a stable hash."""
    schema_json = json.dumps(model.model_json_schema(), sort_keys=True)
    sha = hashlib.sha256(schema_json.encode("utf-8")).hexdigest()

    url = os.getenv("SCHEMA_REGISTRY_URL")
    if not url:
        return sha

    body = json.dumps({"schemaType": "JSON", "schema": schema_json}).encode("utf-8")
    req = request.Request(
        f"{url.rstrip('/')}/subjects/{subject}/versions",
        data=body,
        headers={"Content-Type": "application/vnd.schemaregistry.v1+json"},
        method="POST",
    )
    try:  # pragma: no cover - network interaction
        request.urlopen(req)
    except Exception as exc:  # pragma: no cover - ignore network failures
        logger.warning("schema registry registration failed: %s", exc)
    return sha
