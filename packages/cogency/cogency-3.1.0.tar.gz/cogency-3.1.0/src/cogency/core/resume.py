"""WebSocket streaming with tool injection and session persistence.

Algorithm:
1. Establish WebSocket session with initial context
2. Stream tokens continuously from LLM
3. When parser detects §execute → pause stream → execute tool
4. Inject tool result back into same session → resume streaming
5. Repeat until §end or natural completion

Enables maximum token efficiency by maintaining conversation state
in LLM memory rather than resending full context each turn.
"""

import json
import time

from .. import context
from ..lib import telemetry
from ..lib.metrics import Metrics
from .accumulator import Accumulator
from .config import Config
from .parser import parse_tokens
from .protocols import event_content, event_type, is_end


async def stream(
    query: str,
    user_id: str,
    conversation_id: str,
    *,
    config: Config,
    chunks: bool = False,
):
    """WebSocket streaming with tool injection and session continuity."""

    llm = config.llm
    if llm is None:
        raise ValueError("LLM provider required")

    # Verify WebSocket capability
    if not hasattr(llm, "connect"):
        raise RuntimeError(
            f"Resume mode requires WebSocket support. Provider {type(llm).__name__} missing connect() method. "
            f"Use mode='auto' for fallback behavior or mode='replay' for HTTP-only."
        )

    # Initialize metrics tracking
    model_name = getattr(llm, "http_model", "unknown")
    metrics = Metrics.init(model_name)

    session = None
    try:
        messages = await context.assemble(
            user_id,
            conversation_id,
            tools=config.tools,
            storage=config.storage,
            history_window=config.history_window,
            profile_enabled=config.profile,
            identity=config.identity,
            instructions=config.instructions,
        )

        # Track this LLM call
        if metrics:
            metrics.start_step()
            metrics.add_input(messages)

        time.time()
        json.dumps(messages)
        telemetry_events: list[dict] = []

        session = await llm.connect(messages)

        complete = False

        accumulator = Accumulator(
            user_id,
            conversation_id,
            execution=config.execution,
            chunks=chunks,
        )

        try:
            # All messages (including current query) loaded in connect()
            # Send empty string to trigger response generation
            async for event in accumulator.process(parse_tokens(session.send(""))):
                ev_type = event_type(event)
                content = event_content(event)

                if ev_type in {"think", "call", "respond"} and metrics and content:
                    metrics.add_output(content)

                if event:
                    telemetry.add_event(telemetry_events, event)

                match ev_type:
                    case "end":
                        complete = True
                        # Close session on task completion
                        metric = metrics.event()
                        telemetry.add_event(telemetry_events, metric)
                        yield metric

                    case "execute":
                        if metrics:
                            metric = metrics.event()
                            telemetry.add_event(telemetry_events, metric)
                            yield metric
                            metrics.start_step()

                    case "result":
                        # Yield tool result to user first
                        yield event

                        # Then send tool result to session to continue generation
                        try:
                            if metrics:
                                metrics.add_input(content)

                            # Continue streaming after tool result injection
                            async for continuation_event in accumulator.process(
                                parse_tokens(session.send(content))
                            ):
                                yield continuation_event
                                if is_end(continuation_event):
                                    complete = True
                                    break
                        except Exception as e:
                            raise RuntimeError(f"WebSocket continuation failed: {e}") from e

                        if metrics:
                            metric = metrics.event()
                            telemetry.add_event(telemetry_events, metric)
                            yield metric
                            metrics.start_step()

                        # Skip unconditional yield since we already yielded the result
                        continue

                yield event

                if complete:
                    break
        except Exception:
            raise
        finally:
            if hasattr(config.storage, "save_request"):
                telemetry.persist_events(conversation_id, telemetry_events)

        # Handle natural WebSocket completion
        if not complete:
            # Stream ended without §end - provider-driven completion
            complete = True

    except Exception as e:
        raise RuntimeError(f"WebSocket failed: {str(e)}") from e
    finally:
        # Always cleanup WebSocket session
        if session:
            await session.close()
