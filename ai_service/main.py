import asyncio
import os
import time
from typing import List, Optional

from fastapi import BackgroundTasks, FastAPI
from pydantic import BaseModel

import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "gutumanu.settings")
django.setup()

from tracking.models import AIJob, InferenceRun  # noqa: E402
from .kafka import ScoreSink  # noqa: E402

try:  # pragma: no cover - optional dependency
    import ray
    from ray import serve
except Exception:  # pragma: no cover - ray not installed
    ray = None  # type: ignore

app = FastAPI()
sink = ScoreSink()


class InferenceRequest(BaseModel):
    features: List[float]
    expected: Optional[float] = None


async def _invoke_model(model: str, features: List[float]) -> float:
    """Send features to Ray Serve or return a dummy score."""
    if ray:
        try:  # pragma: no cover - depends on external service
            handle = serve.get_app_handle(model)
            ref = await handle.remote(features)
            return await ref
        except Exception:
            pass
    # Fallback dummy score
    return 0.0


def _record_run(job: AIJob, model: str, score: float, latency: float, expected: Optional[float]) -> None:
    accuracy = None
    drift = None
    if expected is not None:
        accuracy = 1.0 if score == expected else 0.0
        drift = score - expected
    InferenceRun.objects.create(
        job=job,
        model_name=model,
        score=score,
        latency_ms=latency,
        accuracy=accuracy,
        drift=drift,
    )
    sink.publish({"model": model, "score": score})


def _process(job_id: int, model: str, req: InferenceRequest) -> None:
    start = time.perf_counter()
    score = asyncio.run(_invoke_model(model, req.features))
    latency_ms = (time.perf_counter() - start) * 1000
    job = AIJob.objects.get(id=job_id)
    _record_run(job, model, score, latency_ms, req.expected)
    job.status = "completed"
    job.save(update_fields=["status"])


@app.post("/v1/ai/infer/{model}")
async def infer(model: str, request: InferenceRequest, background: BackgroundTasks):
    job = AIJob.objects.create(name=model)
    background.add_task(_process, job.id, model, request)
    return {"job_id": job.id, "status": "submitted"}
