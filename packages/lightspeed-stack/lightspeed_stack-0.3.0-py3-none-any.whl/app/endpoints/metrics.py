"""Handler for REST API call to provide metrics."""

from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.responses import PlainTextResponse
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    generate_latest,
)

from authentication import get_auth_dependency
from authentication.interface import AuthTuple
from authorization.middleware import authorize
from metrics.utils import setup_model_metrics
from models.config import Action

router = APIRouter(tags=["metrics"])


@router.get("/metrics", response_class=PlainTextResponse)
@authorize(Action.GET_METRICS)
async def metrics_endpoint_handler(
    auth: Annotated[AuthTuple, Depends(get_auth_dependency())],
    request: Request,
) -> PlainTextResponse:
    """
    Handle request to the /metrics endpoint.

    Process GET requests to the /metrics endpoint, returning the
    latest Prometheus metrics in form of a plain text.

    Initializes model metrics on the first request if not already
    set up, then responds with the current metrics snapshot in
    Prometheus format.
    """
    # Used only for authorization
    _ = auth

    # Nothing interesting in the request
    _ = request

    # Setup the model metrics if not already done. This is a one-time setup
    # and will not be run again on subsequent calls to this endpoint
    await setup_model_metrics()
    return PlainTextResponse(generate_latest(), media_type=CONTENT_TYPE_LATEST)
