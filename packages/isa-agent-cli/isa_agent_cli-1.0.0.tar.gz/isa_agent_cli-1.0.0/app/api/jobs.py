#!/usr/bin/env python3
"""
Background Jobs API - Polling and SSE streaming endpoints
"""

import json
import asyncio
from typing import AsyncIterator
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from sse_starlette.sse import EventSourceResponse
import redis.asyncio as aioredis

from ..services.background_job_service import get_job_status, get_celery_task_status
from ..config import settings
from ..utils.logger import api_logger

router = APIRouter(prefix="/api/v1/jobs", tags=["background-jobs"])


@router.get("/{job_id}")
async def get_job_status_endpoint(job_id: str):
    """
    Get current status of background job

    Args:
        job_id: Job ID to query

    Returns:
        Job status dict
    """
    api_logger.info(f"job_status_query | job_id={job_id}")

    status = get_job_status(job_id)

    if status.get("status") == "not_found":
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

    return status


@router.get("/{job_id}/celery")
async def get_celery_task_status_endpoint(job_id: str):
    """
    Get Celery task status for job

    Args:
        job_id: Job ID to query

    Returns:
        Celery task status
    """
    job_status = get_job_status(job_id)

    if job_status.get("status") == "not_found":
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

    celery_task_id = job_status.get("celery_task_id")
    if not celery_task_id:
        raise HTTPException(status_code=400, detail="No Celery task ID for this job")

    celery_status = get_celery_task_status(celery_task_id)
    return celery_status


@router.get("/{job_id}/stream")
async def stream_job_progress(job_id: str):
    """
    Stream job progress via Server-Sent Events (SSE)

    Args:
        job_id: Job ID to stream

    Returns:
        SSE stream of job progress
    """
    api_logger.info(f"job_stream_start | job_id={job_id}")

    # Verify job exists
    status = get_job_status(job_id)
    if status.get("status") == "not_found":
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

    async def event_generator() -> AsyncIterator[dict]:
        """Generate SSE events from Redis pub/sub"""
        # Connect to Redis pub/sub
        redis = await aioredis.from_url(
            f"redis://{settings.redis_host}:{settings.redis_port}/2",
            encoding="utf-8",
            decode_responses=True
        )

        pubsub = redis.pubsub()
        channel = f"job_progress:{job_id}"

        try:
            await pubsub.subscribe(channel)
            api_logger.info(f"job_stream_subscribed | job_id={job_id} | channel={channel}")

            # Send initial status
            initial_status = get_job_status(job_id)
            yield {
                "event": "job_status",
                "data": json.dumps(initial_status)
            }

            # Listen for progress updates
            timeout_count = 0
            max_timeouts = 30  # 30 seconds of no activity = close stream

            while True:
                try:
                    # Wait for message with timeout
                    message = await asyncio.wait_for(
                        pubsub.get_message(ignore_subscribe_messages=True),
                        timeout=1.0
                    )

                    if message and message['type'] == 'message':
                        timeout_count = 0  # Reset timeout counter

                        progress_data = json.loads(message['data'])

                        # Determine event type
                        event_type = progress_data.get("type", "progress")

                        yield {
                            "event": event_type,
                            "data": json.dumps(progress_data)
                        }

                        # Check if job is complete
                        if event_type in ["job_complete", "job_error"]:
                            api_logger.info(
                                f"job_stream_complete | "
                                f"job_id={job_id} | "
                                f"final_status={event_type}"
                            )
                            break

                    else:
                        # No message received, increment timeout
                        timeout_count += 1
                        if timeout_count >= max_timeouts:
                            api_logger.warning(
                                f"job_stream_timeout | "
                                f"job_id={job_id} | "
                                f"no_activity_seconds={max_timeouts}"
                            )
                            break

                        # Send heartbeat every 5 seconds
                        if timeout_count % 5 == 0:
                            yield {
                                "event": "heartbeat",
                                "data": json.dumps({
                                    "type": "heartbeat",
                                    "timestamp": asyncio.get_event_loop().time()
                                })
                            }

                except asyncio.TimeoutError:
                    # Timeout waiting for message (expected)
                    continue

                except Exception as e:
                    api_logger.error(
                        f"job_stream_error | "
                        f"job_id={job_id} | "
                        f"error={str(e)}",
                        exc_info=True
                    )
                    yield {
                        "event": "error",
                        "data": json.dumps({"error": str(e)})
                    }
                    break

        finally:
            await pubsub.unsubscribe(channel)
            await redis.close()
            api_logger.info(f"job_stream_closed | job_id={job_id}")

    return EventSourceResponse(event_generator())


@router.post("/{job_id}/cancel")
async def cancel_job(job_id: str):
    """
    Cancel a running background job

    Args:
        job_id: Job ID to cancel

    Returns:
        Cancellation status
    """
    api_logger.info(f"job_cancel_request | job_id={job_id}")

    job_status = get_job_status(job_id)

    if job_status.get("status") == "not_found":
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

    celery_task_id = job_status.get("celery_task_id")
    if not celery_task_id:
        raise HTTPException(status_code=400, detail="No Celery task ID for this job")

    # Cancel Celery task
    from ..services.background_job_service import celery_app
    celery_app.control.revoke(celery_task_id, terminate=True)

    # Update job status
    from ..services.background_job_service import update_job_status
    from datetime import datetime

    update_job_status(job_id, {
        "status": "cancelled",
        "cancelled_at": datetime.now().isoformat()
    })

    api_logger.info(
        f"job_cancelled | "
        f"job_id={job_id} | "
        f"celery_task_id={celery_task_id}"
    )

    return {
        "success": True,
        "job_id": job_id,
        "celery_task_id": celery_task_id,
        "status": "cancelled"
    }
