import asyncio
import json
import traceback
import uuid
from collections.abc import Callable
from datetime import datetime
from typing import TYPE_CHECKING, Any, TypeVar

from fastapi import HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from .constants import CANCEL_GRACE_PERIOD_S
from .exceptions import (
    EventTimeoutError,
    LoopClaimError,
    LoopContextSwitchError,
    LoopPausedError,
    LoopStoppedError,
)
from .logging import setup_logger
from .state.state import LoopState, StateManager
from .types import BaseConfig, LoopEventSender, LoopStatus
from .utils import get_func_import_path

if TYPE_CHECKING:
    from .context import LoopContext

logger = setup_logger(__name__)


class LoopEvent(BaseModel):
    loop_id: str | None = None
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    partial: bool = False
    type: str = Field(default_factory=lambda: getattr(LoopEvent, "type", ""))
    sender: LoopEventSender = LoopEventSender.CLIENT
    timestamp: float = Field(default_factory=lambda: datetime.now().timestamp())
    nonce: int | None = None

    def __init__(self, **data: Any) -> None:
        if "type" not in data and hasattr(self.__class__, "type"):
            data["type"] = self.__class__.type
        super().__init__(**data)

    def to_dict(self) -> dict[str, Any]:
        data = self.model_dump()
        return data

    def to_string(self) -> str:
        return json.dumps(self.to_dict(), default=str)

    def to_json(self) -> str:
        return self.__dict__.copy()  # type: ignore

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "LoopEvent":
        return cls.model_validate(data)

    @classmethod
    def from_json(cls, data: str) -> "LoopEvent":
        dict_data = json.loads(data)
        return cls.from_dict(dict_data)


C = TypeVar("C", bound="LoopContext")


class LoopManager:
    def __init__(self, config: BaseConfig, state_manager: StateManager):
        self.loop_tasks: dict[str, asyncio.Task[None]] = {}
        self.config: BaseConfig = config
        self.state_manager: StateManager = state_manager

    async def _run(
        self,
        func: Callable[..., Any],
        context: Any,
        loop_id: str,
        delay: float,
        loop_stop_func: Callable[..., Any] | None,
    ) -> None:
        try:
            async with self.state_manager.with_claim(loop_id):  # type: ignore
                idle_cycles = 0

                while not context.should_stop and not context.should_pause:
                    context.event_this_cycle = False

                    try:
                        if asyncio.iscoroutinefunction(func):
                            await func(context)
                        else:
                            func(context)  # type: ignore
                    except asyncio.CancelledError:
                        logger.info(
                            "Loop task cancelled, exiting",
                            extra={"loop_id": loop_id},
                        )
                        break
                    except LoopContextSwitchError as e:
                        func = e.func
                        context = e.context
                        loop = await self.state_manager.get_loop(loop_id)
                        loop.current_function_path = get_func_import_path(func)
                        await self.state_manager.update_loop(loop_id, loop)
                        continue
                    except EventTimeoutError:
                        ...
                    except (LoopPausedError, LoopStoppedError):
                        raise
                    except BaseException as e:
                        logger.error(
                            "Unhandled exception in loop",
                            extra={
                                "loop_id": loop_id,
                                "error": str(e),
                                "traceback": traceback.format_exc(),
                            },
                        )

                    if not context.event_this_cycle:
                        idle_cycles += 1
                        if (
                            idle_cycles >= self.config.max_idle_cycles
                            and self.config.shutdown_idle
                        ):
                            raise LoopPausedError()
                    else:
                        idle_cycles = 0

                    try:
                        await asyncio.sleep(delay)
                    except asyncio.CancelledError:
                        logger.info(
                            "Task cancelled during sleep, exiting",
                            extra={"loop_id": loop_id},
                        )
                        break

                if context.should_stop:
                    raise LoopStoppedError()
                elif context.should_pause:
                    raise LoopPausedError()

        except asyncio.CancelledError:
            logger.info("Loop task cancelled, exiting", extra={"loop_id": loop_id})
        except LoopClaimError:
            logger.info("Loop claim error, exiting", extra={"loop_id": loop_id})
        except LoopStoppedError:
            logger.info(
                "Loop stopped",
                extra={"loop_id": loop_id},
            )
            await self.state_manager.update_loop_status(loop_id, LoopStatus.STOPPED)
        except LoopPausedError:
            logger.info(
                "Loop paused",
                extra={"loop_id": loop_id},
            )
            await self.state_manager.update_loop_status(loop_id, LoopStatus.IDLE)
        finally:
            if loop_stop_func:
                if asyncio.iscoroutinefunction(loop_stop_func):
                    await loop_stop_func(context)
                else:
                    loop_stop_func(context)  # type: ignore

            self.loop_tasks.pop(loop_id, None)

    async def start(
        self,
        *,
        func: Callable[..., Any],
        loop_start_func: Callable[..., Any] | None,
        loop_stop_func: Callable[..., Any] | None,
        context: Any,
        loop: LoopState,
        loop_delay: float = 0.1,
    ) -> bool:
        if loop.loop_id in self.loop_tasks:
            return False

        if loop_start_func:
            if asyncio.iscoroutinefunction(loop_start_func):
                await loop_start_func(context)
            else:
                loop_start_func(context)  # type: ignore

        # TODO: switch out executor for thread/process based on config
        self.loop_tasks[loop.loop_id] = asyncio.create_task(
            self._run(func, context, loop.loop_id, loop_delay, loop_stop_func)
        )

        return True

    async def stop(self, loop_id: str) -> bool:
        task = self.loop_tasks.pop(loop_id, None)
        if task:
            task.cancel()

            try:
                await asyncio.wait_for(task, timeout=CANCEL_GRACE_PERIOD_S)
            except TimeoutError:
                logger.warning(
                    "Loop task did not stop within timeout",
                    extra={"loop_id": loop_id},
                )

            return True

        return False

    async def stop_all(self):
        """Stop all running loop tasks and wait for them to complete."""

        tasks_to_cancel = list(self.loop_tasks.values())
        self.loop_tasks.clear()

        for task in tasks_to_cancel:
            task.cancel()

        # Wait for all loop tasks to complete (w/ timeout)
        if tasks_to_cancel:
            try:
                await asyncio.wait_for(
                    asyncio.gather(*tasks_to_cancel, return_exceptions=True),
                    timeout=CANCEL_GRACE_PERIOD_S,
                )
            except TimeoutError:
                logger.warning(
                    "Some loop tasks did not complete within timeout",
                    extra={"tasks": [task.get_name() for task in tasks_to_cancel]},
                )
            except BaseException as e:
                logger.error(
                    "Error waiting for loop tasks to complete",
                    extra={"error": str(e)},
                )

    async def active_loop_ids(self) -> set[str]:
        """
        Returns a set of loop IDs with tasks that are currently running in this replica.
        """

        return {loop_id for loop_id, _ in self.loop_tasks.items()}

    async def events_sse(self, loop_id: str):
        """
        SSE endpoint for streaming events to clients.
        """
        loop = await self.state_manager.get_loop(loop_id)
        if not loop:
            raise HTTPException(status_code=404, detail="Loop not found")

        connection_time = int(datetime.now().timestamp())
        last_sent_nonce = 0
        connection_id = str(uuid.uuid4())

        await self.state_manager.register_client_connection(loop_id, connection_id)
        pubsub = await self.state_manager.subscribe_to_events(loop_id)

        async def _event_generator():
            nonlocal last_sent_nonce

            try:
                while True:
                    all_events: list[
                        dict[str, Any]
                    ] = await self.state_manager.get_events_since(
                        loop_id, connection_time
                    )
                    server_events = [
                        e
                        for e in all_events
                        if e["sender"] == LoopEventSender.SERVER.value
                        and e["nonce"] > last_sent_nonce
                    ]

                    # Send any new events
                    for event in server_events:
                        event_data = json.dumps(event)
                        yield f"data: {event_data}\n\n"
                        last_sent_nonce = max(last_sent_nonce, event["nonce"])

                    # If no events, wait for notification or timeout
                    if not server_events:
                        # Wait for either a new event notification or keepalive timeout
                        notification_received = (
                            await self.state_manager.wait_for_event_notification(
                                pubsub, timeout=self.config.sse_keep_alive_s
                            )
                        )

                        if not notification_received:
                            yield "data: keepalive\n\n"

                        # Refresh connection TTL periodically
                        await self.state_manager.refresh_client_connection(
                            loop_id, connection_id
                        )

            except asyncio.CancelledError:
                pass
            except BaseException as e:
                logger.error(
                    "Error in SSE stream for loop",
                    extra={
                        "loop_id": loop_id,
                        "error": str(e),
                        "traceback": traceback.format_exc(),
                    },
                )
                yield f'data: {{"type": "error", "message": "{e!s}"}}\n\n'
            finally:
                await self.state_manager.unregister_client_connection(
                    loop_id, connection_id
                )
                if pubsub is not None:
                    await pubsub.unsubscribe()  # type: ignore
                    await pubsub.close()  # type: ignore

        return StreamingResponse(
            _event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Headers": "Cache-Control",
            },
        )
