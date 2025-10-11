import asyncio
from contextlib import AbstractAsyncContextManager
from dataclasses import dataclass
import logging
from typing import (
    Annotated,
    Any,
    AsyncGenerator,
    Dict,
    List,
    Optional,
    Tuple,
    Callable,
    cast,
    get_args,
)
from uuid import uuid4

from fastapi import Depends, HTTPException, Request, APIRouter
from fastapi.responses import StreamingResponse
from langchain_core.callbacks import AsyncCallbackHandler
from langchain_core.runnables import RunnableConfig
from langgraph.graph import MessagesState
from langgraph.graph.state import CompiledStateGraph
from langgraph.types import StateSnapshot
import langchain_core.messages as langchain_messages
from pydantic import BaseModel, RootModel

from .schema import (
    AbstractStreamPayload,
    AnyMessage as AnyMessage_,
    AnyMessageChunk as AnyMessageChunk_,
    HumanMessage,
    StreamDone,
    StreamError,
    AnyStreamEvent as AnyStreamEvent_,
    StreamInput,
    InvokeInput,
    StreamMessage,
    StreamMessageChunk,
    StreamWarning,
    ToolMessageChunk,
    api_message_chunk_from_langchain,
    api_message_from_langchain,
)
from veri_agents_api.threads_util import ThreadInfo, ThreadsCheckpointerUtil
from veri_agents_api.util.awaitable import as_awaitable, MaybeAwaitable

log = logging.getLogger(__name__)


class TokenQueueStreamingHandler(AsyncCallbackHandler):
    """LangChain callback handler for streaming LLM tokens to an asyncio queue."""

    def __init__(self, queue: asyncio.Queue):
        self.queue = queue

    async def on_llm_new_token(self, token: str, **kwargs) -> None:
        if token:
            await self.queue.put(token)


class AnyMessage(RootModel[AnyMessage_]):
    pass

class AnyMessageChunk(RootModel[AnyMessageChunk_]):
    pass

class AnyStreamEvent(RootModel[AnyStreamEvent_]):
    pass

class ChatHistory(RootModel[list[AnyMessage]]):
    pass


@dataclass
class ThreadContext:
    id: str
    graph: CompiledStateGraph
    config: Optional[RunnableConfig] = None


def create_thread_router(
    *,
    get_thread: Callable[..., AbstractAsyncContextManager[ThreadContext]],
    on_new_thread: Callable[
        [str, ThreadInfo | None, InvokeInput, Request], MaybeAwaitable[None]
    ] = lambda thread_id, thread_info, invoke_input, request: None,
    # transform_state: Callable[[dict[str, Any] | Any], dict[str, Any] | Any] | None = None,
    # InvokeInputCls: Type[InvokeInput] = InvokeInput,
    **router_kwargs,
):
    """
    POST /invoke
    POST /stream
    GET /history
    GET /feedback
    POST /feedback
    """

    router = APIRouter(**router_kwargs)

    def _parse_input(
        user_input: InvokeInput,
        thread_id: str,
        invoke_recvd_runnable_config: RunnableConfig | None,
    ) -> Tuple[Dict[str, Any], str]:
        run_id = uuid4()
        input_message = HumanMessage(content=user_input.message)

        runnable_config = invoke_recvd_runnable_config or RunnableConfig()

        runnable_config["configurable"] = {
            **{
                # used by checkpointer
                "thread_id": thread_id,
                "_has_threadinfo": True,
                # "args": user_input.args,
            },
            **(runnable_config.get("configurable", {})),
        }

        kwargs = dict(
            input={"messages": [input_message.to_langchain()]}, config=runnable_config
        )
        return kwargs, str(run_id)

    @router.post("/invoke")
    async def invoke(
        invoke_input: InvokeInput,
        request: Request,
        thread_ctx_mngr: Annotated[
            AbstractAsyncContextManager[ThreadContext], Depends(get_thread)
        ],
    ) -> AnyMessage:
        """
        Invoke the agent with user input to retrieve a final response.

        Use thread_id to persist and continue a multi-turn conversation. run_id kwarg
        is also attached to messages for recording feedback.
        """

        async with thread_ctx_mngr as thread_ctx:
            thread_info = await ThreadsCheckpointerUtil.get_thread_info(
                thread_ctx.id, thread_ctx.graph.checkpointer
            )
            kwargs, run_id = _parse_input(
                invoke_input, thread_ctx.id, thread_ctx.config
            )

            await as_awaitable(
                on_new_thread(thread_ctx.id, thread_info, invoke_input, request)
            )

            # do transformation
            state_snapshot = await thread_ctx.graph.aget_state(kwargs["config"])
            state = cast(MessagesState, state_snapshot.values)
            # if transform_state:
            #     transformed = transform_state(state)
            #     if transformed != state:
            #         await thread_ctx.graph.aupdate_state(kwargs["config"], transformed)
            #         state = transformed

            try:
                response = cast(MessagesState, await thread_ctx.graph.ainvoke(**kwargs))
                output = api_message_from_langchain(response["messages"][-1])
                # output.run_id = str(run_id) # FIXME?
                return AnyMessage(output)
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

    @router.post("/stream", responses={
            "200": {
                "description": "Server-Sent Events stream",
                "content": {
                    "text/event-stream": {
                        "schema": {
                            "type": "object",
                            "description": "SSE Event Stream - sends multiple events",
                            "oneOf": [
                                {"$ref": f"#/components/schemas/{cast(type[BaseModel], EventType).model_json_schema()["title"]}"} for EventType in list(get_args(AnyStreamEvent))
                            ],
                        }
                    }
                },
            }
        })
    async def stream(
        stream_input: StreamInput,
        request: Request,
        thread_ctx_mngr: Annotated[
            AbstractAsyncContextManager[ThreadContext], Depends(get_thread)
        ]
    ) -> StreamingResponse:
        """
        Stream the agent's response to a user input, including intermediate messages and tokens.

        Use thread_id to persist and continue a multi-turn conversation. run_id kwarg
        is also attached to all messages for recording feedback.
        """

        async def message_generator() -> AsyncGenerator[AbstractStreamPayload, None]:
            """
            Generate a stream of messages from the agent.

            This is the workhorse method for the /stream endpoint.
            """
            async with thread_ctx_mngr as thread_ctx:

                thread_info = await ThreadsCheckpointerUtil.get_thread_info(
                    thread_ctx.id, thread_ctx.graph.checkpointer
                )

                kwargs, run_id = _parse_input(
                    stream_input, thread_ctx.id, thread_ctx.config
                )

                await as_awaitable(
                    on_new_thread(thread_ctx.id, thread_info, stream_input, request)
                )

                # # do transformation
                # state_snapshot = await thread_ctx.graph.aget_state(kwargs["config"])
                # state = state_snapshot.values
                # if transform_state:
                #     transformed = transform_state(state)
                #     if transformed != state:
                #         await thread_ctx.graph.aupdate_state(kwargs["config"], transformed)
                #         state = transformed

                # Process the queue and yield messages over the SSE stream.
                async for stream_mode, chunk in thread_ctx.graph.astream(
                    **kwargs, stream_mode=["updates", "messages", "custom"]
                ):
                    log.info(
                        "Got from queue: %s %s: %s", stream_mode, type(chunk), chunk
                    )

                    try:
                        if stream_mode == "messages":
                            message_chunk = cast(
                                str | langchain_messages.AnyMessage, chunk[0]
                            )
                            metadata = cast(dict[str, Any], chunk[1])

                            try:
                                api_message_chunk = api_message_chunk_from_langchain(
                                    message_chunk
                                )
                            except Exception as e:
                                yield StreamError(
                                    content=f"Error parsing message chunk: {e}"
                                )
                                continue

                            yield StreamMessageChunk(content=api_message_chunk)
                        elif stream_mode == "updates":
                            (s,) = cast(Any, chunk).values()  # TODO: fix any
                            state = cast(MessagesState, s)

                            new_messages = state["messages"]
                            for message in new_messages:
                                # LangGraph re-sends the input message, which feels weird, so drop it
                                if (
                                    message.type == "human"
                                    and message.content == stream_input.message
                                ):
                                    continue

                                try:
                                    api_message = api_message_from_langchain(message)
                                    # chat_message.run_id = str(run_id) # FIXME?
                                except Exception as e:
                                    yield StreamError(
                                        content=f"Error parsing message: {e}"
                                    )
                                    continue

                                yield StreamMessage(content=api_message)
                        elif stream_mode == "custom":
                            if isinstance(chunk, ToolMessageChunk):
                                yield StreamMessageChunk(content=chunk)
                            else:
                                yield StreamWarning(
                                    content=f'unsupported custom chunk: "{type(chunk)}: {chunk}"'
                                )
                        else:
                            yield StreamWarning(
                                content=f'unsupported stream_mode: "{stream_mode}"'
                            )
                    except Exception as e:
                        yield StreamError(content=f"Error: {e}")
                        continue

                yield StreamDone()

        return StreamingResponse(
            (payload.__str__() async for payload in message_generator()),
            media_type="text/event-stream",
        )

    @router.get("/history")
    async def history(
        request: Request,
        thread_ctx_mngr: Annotated[
            AbstractAsyncContextManager[ThreadContext], Depends(get_thread)
        ],
    ) -> ChatHistory:
        """
        Get the history of a thread.
        """

        async with thread_ctx_mngr as thread_ctx:

            config = RunnableConfig(
                configurable={
                    # used by checkpointer
                    "thread_id": thread_ctx.id,
                }
            )

            # # do transformation
            state_snapshot = await thread_ctx.graph.aget_state(config)
            state = cast(MessagesState, state_snapshot.values)
            # if transform_state:
            #     transformed = transform_state(state)
            #     if transformed != state:
            #         await thread_ctx.graph.aupdate_state(config, transformed)
            #         state = transformed

            messages = state.get("messages", [])

            converted_messages: List[AnyMessage_] = []
            for message in messages:
                try:
                    chat_message = api_message_from_langchain(message)
                    converted_messages.append(chat_message)
                except Exception as e:
                    log.error(f"Error parsing message: {e}")
                    continue
            return ChatHistory([AnyMessage(msg) for msg in converted_messages])

    @router.get("/internal/_schema/stream", response_model=
                                    AnyStreamEvent
                                )
    async def _openapi_schema_stream():
        pass

    @router.get("/internal/_schema/message", response_model=
                                    AnyMessage
                                )
    async def _openapi_schema_message():
        pass

    @router.get("/internal/_schema/message_chunk", response_model=
                                    AnyMessageChunk
                                )
    async def _openapi_schema_message_chunk():
        pass

    return router
