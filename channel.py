# from typing import Text, List, Dict, Any, Optional, Callable, Iterable, Awaitable , NoReturn
# from asyncio import Queue, CancelledError
# from sanic.request import Request
# from rasa.core.channels import InputChannel
from rasa.core.agent import Agent
from rasa.core.interpreter import RasaNLUInterpreter
# from rasa.core.channels.channel import UserMessage, CollectingOutputChannel #QueueOutputChannel
from rasa.utils.endpoints import EndpointConfig
from rasa import utils
# from sanic import Blueprint, response
from rasa.model import get_model, get_model_subdirectories
# import inspect
from rasa.core.run import configure_app
import asyncio
import inspect
import json
import logging

# logger = logging.getLogger(__name__)


# class RestInput(InputChannel):
#     #A custom http input channel.
#     #This implementation is the basis for a custom implementation of a chat
#     #frontend. You can customize this to send messages to Rasa Core and
#     #retrieve responses from the agent.

#     @classmethod
#     def name(cls):
#         return "rest"

#     @staticmethod
#     async def on_message_wrapper(
#         on_new_message: Callable[[UserMessage], Awaitable[None]],
#         text: Text,
#         queue: Queue,
#         sender_id: Text,
#         input_channel: Text,
#     ) -> None:
#         collector = QueueOutputChannel(queue)
#         message = UserMessage(text, collector, sender_id, input_channel=input_channel)
#         await on_new_message(message)
#         await queue.put("DONE")  # pytype: disable=bad-return-type

#     async def _extract_sender(self, req: Request) -> Optional[Text]:
#         return req.json.get("sender", None)

#     # noinspection PyMethodMayBeStatic
#     def _extract_message(self, req: Request) -> Optional[Text]:
#         return req.json.get("message", None)

#     def _extract_input_channel(self, req: Request) -> Text:
#         return req.json.get("input_channel") or self.name()

#     def stream_response(
#         self,
#         on_new_message: Callable[[UserMessage], Awaitable[None]],
#         text: Text,
#         sender_id: Text,
#         input_channel: Text,
#     ) -> Callable[[Any], Awaitable[None]]:
#         async def stream(resp: Any) -> None:
#             q = Queue()
#             task = asyncio.ensure_future(
#                 self.on_message_wrapper(
#                     on_new_message, text, q, sender_id, input_channel
#                 )
#             )
#             result = None  # declare variable up front to avoid pytype error
#             while True:
#                 result = await q.get()
#                 if result == "DONE":
#                     break
#                 else:
#                     await resp.write(json.dumps(result) + "\n")
#             await task
#         return stream  # pytype: disable=bad-return-type

#     def blueprint(self, on_new_message: Callable[[UserMessage], Awaitable[None]]):
#         custom_webhook = Blueprint(
#             "mycustom_webhook_{}".format(type(self).__name__),
#             inspect.getmodule(self).__name__,
#         )
#         @custom_webhook.route("/", methods=["GET"])
#         async def health(request: Request):
#             return response.json({"status": "ok"})
#         @custom_webhook.route("/webhook", methods=["POST"])
#         async def receive(request: Request):
#             sender_id = await self._extract_sender(request)
#             text = self._extract_message(request)
#             should_use_stream = utils.endpoints.bool_arg(
#                 request, "stream", default=False
#             )
#             input_channel = self._extract_input_channel(request)

#             if should_use_stream:
#                 return response.stream(
#                     self.stream_response(
#                         on_new_message, text, sender_id, input_channel
#                     ),
#                     content_type="text/event-stream",
#                 )
#             else:
#                 collector = CollectingOutputChannel()
#                 # noinspection PyBroadException
#                 try:
#                     await on_new_message(
#                         UserMessage(
#                             text, collector, sender_id, input_channel=input_channel
#                         )
#                     )
#                 except CancelledError:
#                     logger.error(
#                         "Message handling timed out for "
#                         "user message '{}'.".format(text)
#                     )
#                 except Exception:
#                     logger.exception(
#                         "An exception occured while handling "
#                         "user message '{}'.".format(text)
#                     )
#                 return response.json(collector.messages)
#         return custom_webhook


# class QueueOutputChannel(CollectingOutputChannel):
#     """Output channel that collects send messages in a list
#     (doesn't send them anywhere, just collects them)."""

#     @classmethod
#     def name(cls) -> Text:
#         return "queue"

#     # noinspection PyMissingConstructor
#     def __init__(self, message_queue: Optional[Queue] = None) -> None:
#         super().__init__()
#         self.messages = Queue() if not message_queue else message_queue

#     def latest_output(self) -> NoReturn:
#         raise NotImplementedError("A queue doesn't allow to peek at messages.")

#     async def _persist_message(self, message: Dict[Text, Any]) -> None:
#         await self.messages.put(message)


# --------------------------------------------------------------------------------------------------------------------------------


import asyncio
import inspect
from sanic import Sanic, Blueprint, response
from sanic.request import Request
from sanic.response import HTTPResponse
from typing import Text, Dict, Any, Optional, Callable, Awaitable, NoReturn
from asyncio import Queue, CancelledError
import rasa.utils.endpoints
from rasa.core.channels.channel import (
    InputChannel,
    CollectingOutputChannel,
    UserMessage,
)

class MyioInput(InputChannel):
    @classmethod
    def name(cls) -> Text:
        return "myio"


    @staticmethod
    async def on_message_wrapper(
        on_new_message: Callable[[UserMessage], Awaitable[Any]],
        text: Text,
        queue: Queue,
        sender_id: Text,
        input_channel: Text,
        metadata: Optional[Dict[Text, Any]],
    ) -> None:
        collector = QueueOutputChannel(queue)

        message = UserMessage(
            text, collector, sender_id, input_channel=input_channel, metadata=metadata
        )
        await on_new_message(message)

        await queue.put("DONE")

    async def _extract_sender(self, req: Request) -> Optional[Text]:
        return req.json.get("sender", None)

    # noinspection PyMethodMayBeStatic

    def _extract_message(self, req: Request) -> Optional[Text]:
        return req.json.get("message", None)

    def _extract_input_channel(self, req: Request) -> Text:
        return req.json.get("input_channel") or self.name()

    def stream_response(
        self,
        on_new_message: Callable[[UserMessage], Awaitable[None]],
        text: Text,
        sender_id: Text,
        input_channel: Text,
        metadata: Optional[Dict[Text, Any]],
    ) -> Callable[[Any], Awaitable[None]]:
        async def stream(resp: Any) -> None:
            q = Queue()
            task = asyncio.ensure_future(
                self.on_message_wrapper(
                    on_new_message, text, q, sender_id, input_channel, metadata
                )
            )
            while True:
                result = await q.get()
                if result == "DONE":
                    break
                else:
                    await resp.write(json.dumps(result) + "\n")
            await task

        return stream



    def blueprint(
        self, on_new_message: Callable[[UserMessage], Awaitable[None]]
    ) -> Blueprint:
        custom_webhook = Blueprint(
            "custom_webhook_{}".format(type(self).__name__),
            inspect.getmodule(self).__name__,
        )

        # noinspection PyUnusedLocal
        @custom_webhook.route("/", methods=["GET"])
        async def health(request: Request) -> HTTPResponse:
            return response.json({"status": "ok"})

        @custom_webhook.route("/webhook", methods=["POST"])
        async def receive(request: Request) -> HTTPResponse:
            sender_id = await self._extract_sender(request)
            text = self._extract_message(request)
            should_use_stream = rasa.utils.endpoints.bool_arg(
                request, "stream", default=False
            )
            input_channel = self._extract_input_channel(request)
            metadata = self.get_metadata(request)

            if should_use_stream:
                return response.stream(
                    self.stream_response(
                        on_new_message, text, sender_id, input_channel, metadata
                    ),
                    content_type="text/event-stream",
                )
            else:
                collector = MyioOutput()
                # noinspection PyBroadException
                try:
                    await on_new_message(
                        UserMessage(
                            text,
                            collector,
                            sender_id,
                            input_channel=input_channel,
                            metadata=metadata,
                        )
                    )
                except CancelledError:
                    logger.error(
                        f"Message handling timed out for " f"user message '{text}'."
                    )
                except Exception:
                    logger.exception(
                        f"An exception occured while handling "
                        f"user message '{text}'."
                    )
                return response.json(collector.messages)

        return custom_webhook


class MyioOutput(CollectingOutputChannel):
    @classmethod
    def name(cls) -> Text:
        return "myio"




model_path = get_model("/home/janmejay/Rasa bot/bot3/models")

def run(serve_forever=True):
    _, nlu_model = get_model_subdirectories(model_path)
    interpreter = RasaNLUInterpreter(nlu_model)
    action_url = "http://"+ "localhost:5055" + "/webhook"
    action_endpoint = EndpointConfig(url=action_url)
    agent = Agent.load(model_path, interpreter=interpreter, action_endpoint=action_endpoint)
    input_channel = MyioInput()
    if serve_forever:
        configure_app(input_channel)
    return agent


if __name__ == '__main__':
    utils.io.configure_colored_logging(loglevel="INFO")
    run()