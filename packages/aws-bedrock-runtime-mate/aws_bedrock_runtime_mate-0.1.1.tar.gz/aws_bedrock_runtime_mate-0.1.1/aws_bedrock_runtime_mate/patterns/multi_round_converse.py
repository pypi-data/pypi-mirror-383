# -*- coding: utf-8 -*-

"""
Multi-round conversation management for Amazon Bedrock Runtime.

This module provides high-level abstractions for managing multi-turn conversations
with Amazon Bedrock foundation models. It automatically handles conversation history,
message state management, and provides both regular and streaming response modes.

Key Features:

1. **Automatic History Management**: Maintains conversation history across multiple turns
2. **Unified Configuration**: Set default parameters for all API calls in a session
3. **Streaming Support**: Full support for streaming responses with automatic message collection
4. **Debug Mode**: Optional verbose logging for debugging and monitoring
5. **Type Safety**: Full type hints for all conversation operations

The main component is ``ChatSession``, which manages stateful multi-turn conversations
while providing a simple, intuitive API for both regular and streaming interactions.
"""

import typing as T
import json
import hashlib
import dataclasses

from func_args.api import BaseModel
from rich import print as rprint

from ..converse import ConverseKwargs, ConverseResponse, MessageContentBuilder
from ..converse_stream import ConverseStreamOutput, ConverseStreamResponse

if T.TYPE_CHECKING:  # pragma: no cover
    from mypy_boto3_bedrock_runtime import Client
    from mypy_boto3_bedrock_runtime.type_defs import (
        MessageUnionTypeDef,
    )
    from boto3_dataclass_bedrock_runtime.type_defs import (
        ConverseResponse,
    )


def json_hash(obj: T.Any) -> str:
    """
    Generate MD5 hash of a JSON-serializable object for debugging.

    This utility function creates a deterministic hash of any JSON-serializable
    object by converting it to formatted JSON and computing its MD5 digest.
    Useful for tracking message state changes in conversation history.

    Args:
        obj: Any JSON-serializable object (dict, list, str, etc.)

    Returns:
        str: MD5 hash hexdigest of the JSON representation

    Example::

        messages = [{"role": "user", "content": [{"text": "Hello"}]}]
        hash_value = json_hash(messages)
        print(hash_value)  # "a1b2c3d4e5f6..."
    """
    j = json.dumps(obj, ensure_ascii=False, sort_keys=True, indent=4)
    h = hashlib.md5(j.encode("utf-8")).hexdigest()
    return h


@dataclasses.dataclass
class ChatSession(BaseModel):
    """
    Stateful multi-turn conversation manager for Amazon Bedrock Runtime.

    This class manages conversation state across multiple API calls, automatically
    maintaining message history and applying default configuration. It provides
    a simplified interface for building chatbots, conversational AI, and multi-turn
    interactions with Bedrock foundation models.

    **Key Capabilities:**

    - **Conversation History**: Automatically tracks all messages (user and assistant)
    - **Default Configuration**: Apply consistent settings (model, inference config, etc.)
      across all turns
    - **Streaming Support**: Full support for streaming responses with automatic
      message collection
    - **Debug Mode**: Verbose logging for troubleshooting and monitoring
    - **Flexible Overrides**: Override default configuration per-message as needed

    **Architecture:**

    The session maintains an internal message list that grows with each turn.
    Every API call includes the full conversation history, allowing the model
    to maintain context across turns. For streaming responses, the session
    automatically collects the complete message for history after streaming completes.

    Attributes:
        client: AWS Bedrock Runtime client from boto3
        converse_kwargs: Default configuration for all converse API calls
        printer: Custom print function for debug output (default: rich.print)
        verbose: Enable verbose debug logging

    Example::

        import boto3
        from aws_bedrock_runtime_mate.patterns.multi_round_converse import (
            ChatSession,
            ConverseKwargs,
        )

        # Initialize
        client = boto3.client("bedrock-runtime")
        session = ChatSession(
            client=client,
            converse_kwargs=ConverseKwargs(
                model_id="anthropic.claude-3-sonnet-20240229-v1:0",
                inference_config={
                    "temperature": 0.7,
                    "maxTokens": 1000,
                },
            ),
            verbose=True,  # Enable debug logging
        )

        # Simple text conversation
        res1 = session.converse_text("What is the capital of France?")
        print(res1.text)  # "The capital of France is Paris."

        # Streaming response
        res2 = session.converse_text_stream("Tell me more about Paris")
        for text in session.iterate_text(res2):
            print(text, end="", flush=True)

        # Complex message with images
        from aws_bedrock_runtime_mate.converse import MessageContentBuilder

        builder = MessageContentBuilder()
        builder.add_text("What's in this image?")
        builder.add_image(format="png", bytes=image_bytes)
        res3 = session.converse([builder.to_message()])
        print(res3.text)

    See Also:
        - `converse API <https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-runtime/client/converse.html>`_
        - `converse_stream API <https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-runtime/client/converse_stream.html>`_
    """

    # fmt: off
    client: "Client" = dataclasses.field()
    converse_kwargs: ConverseKwargs | None = dataclasses.field(default=None)

    printer: T.Callable = dataclasses.field(default=rprint)
    verbose: bool = dataclasses.field(default=False)

    _messages: list["MessageUnionTypeDef"] = dataclasses.field(init=False)
    # fmt: on

    def __post_init__(self):
        self._messages = []

    def debug(self, msg: str):
        """
        Print debug message if verbose mode is enabled.

        Args:
            msg: The debug message to print
        """
        if self.verbose:
            self.printer(msg)

    def _prepare_kwargs(
        self,
        converse_kwargs: ConverseKwargs | None,
    ) -> dict[str, T.Any]:
        """
        Prepare API kwargs by merging per-call and default configurations.

        This internal method merges the per-call configuration with the session's
        default configuration, with per-call parameters taking precedence.

        Args:
            converse_kwargs: Per-call configuration to override defaults

        Returns:
            dict: Merged kwargs ready for boto3 API call
        """
        if converse_kwargs is None:
            kwargs = {}
        else:
            kwargs = converse_kwargs.to_boto3_kwargs()
        if self.converse_kwargs is None:
            default_kwargs = {}
        else:
            default_kwargs = self.converse_kwargs.to_boto3_kwargs()
        kwargs.update(default_kwargs)
        return kwargs

    def converse(
        self,
        messages: T.Sequence["MessageUnionTypeDef"],
        converse_kwargs: ConverseKwargs | None = None,
    ) -> "ConverseResponse":
        """
        Send one or more messages and receive a non-streaming response.

        This method adds the provided messages to the conversation history,
        sends all accumulated messages to the model, and stores the assistant's
        response in the history. This directly maps to the AWS Bedrock converse API.

        Args:
            messages: One or more message dictionaries to send. Each message
                should have "role" and "content" fields.
            converse_kwargs: Optional configuration to override session defaults
                for this specific call

        Returns:
            ConverseResponse: Enhanced response object with convenient text extraction

        Example::

            from aws_bedrock_runtime_mate.converse import MessageContentBuilder

            # Send simple text
            builder = MessageContentBuilder()
            builder.add_text("What is 2+2?")
            response = session.converse([builder.to_message()])
            print(response.text)  # "2+2 equals 4"

            # Send with custom config
            response = session.converse(
                messages=[builder.to_message()],
                converse_kwargs=ConverseKwargs(
                    inference_config={"temperature": 0.5}
                )
            )
        """
        self._messages.extend(messages)
        messages = self._messages
        hashes = json_hash(messages)
        n_messages = len(messages)
        self.debug(f"===== Send messages, n_msg = {n_messages}, hash = {hashes}")
        kwargs = self._prepare_kwargs(converse_kwargs=converse_kwargs)
        kwargs["messages"] = messages
        self.debug("----- Converse kwargs:")
        self.debug(kwargs)
        response = self.client.converse(**kwargs)
        response = ConverseResponse(boto3_raw_data=response)
        self.debug("----- Converse response:")
        response_metadata = response.boto3_raw_data.pop("ResponseMetadata")
        self.debug(response.boto3_raw_data)
        response.boto3_raw_data["ResponseMetadata"] = response_metadata
        self._messages.append(response.output.message.boto3_raw_data)
        return response

    def converse_text(
        self,
        message: str,
        converse_kwargs: ConverseKwargs | None = None,
    ) -> "ConverseResponse":
        """
        Send a single text message and receive a non-streaming response.

        This is a convenience method that wraps the text in a proper message
        structure and calls ``converse``. Ideal for simple text-only
        interactions.

        Args:
            message: The text message to send
            converse_kwargs: Optional configuration to override session defaults

        Returns:
            ConverseResponse: Enhanced response object with convenient text extraction

        Example::

            session = ChatSession(client=client, converse_kwargs=ConverseKwargs(
                model_id="anthropic.claude-3-sonnet-20240229-v1:0"
            ))

            # First turn
            response = session.converse_text("Hello, how are you?")
            print(response.text)

            # Second turn (maintains context)
            response = session.converse_text("What was my first question?")
            print(response.text)  # Model remembers the conversation
        """
        content_builder = MessageContentBuilder()
        content_builder.add_text(message)
        return self.converse(
            messages=[content_builder.to_message()],
            converse_kwargs=converse_kwargs,
        )

    def converse_stream(
        self,
        messages: T.Sequence["MessageUnionTypeDef"],
        converse_kwargs: ConverseKwargs | None = None,
    ) -> "ConverseStreamResponse":
        """
        Send one or more messages and receive a streaming response.

        This method adds the provided messages to the conversation history and
        initiates a streaming response. The response must be consumed using
        ``iterate_events`` or ``iterate_text`` to automatically collect the
        complete message for conversation history. This directly maps to the AWS
        Bedrock converse_stream API.

        Args:
            messages: One or more message dictionaries to send
            converse_kwargs: Optional configuration to override session defaults

        Returns:
            ConverseStreamResponse: Enhanced streaming response object

        Note:
            After consuming the stream using ``iterate_events`` or ``iterate_text``,
            the session automatically adds the assistant's complete message to the
            conversation history.

        Example::

            from aws_bedrock_runtime_mate.converse import MessageContentBuilder

            builder = MessageContentBuilder()
            builder.add_text("Tell me a story")
            response = session.converse_stream([builder.to_message()])

            # Consume the stream and collect message
            for event in session.iterate_events(response):
                if event.text:
                    print(event.text, end="", flush=True)
        """
        self._messages.extend(messages)
        messages = self._messages
        hashes = json_hash(messages)
        n_messages = len(messages)
        self.debug(f"===== Send messages, n_msg = {n_messages}, hash = {hashes}")
        kwargs = self._prepare_kwargs(converse_kwargs=converse_kwargs)
        kwargs["messages"] = messages
        self.debug("----- Converse kwargs:")
        self.debug(kwargs)
        response = self.client.converse_stream(**kwargs)
        response = ConverseStreamResponse(boto3_raw_data=response)
        self.debug("----- Converse response:")
        response_metadata = response.boto3_raw_data.pop("ResponseMetadata")
        self.debug(response.boto3_raw_data)
        response.boto3_raw_data["ResponseMetadata"] = response_metadata
        # self._messages.append(response.output.message.boto3_raw_data)
        return response

    def converse_text_stream(
        self,
        message: str,
        converse_kwargs: ConverseKwargs | None = None,
    ) -> "ConverseStreamResponse":
        """
        Send a single text message and receive a streaming response.

        This is a convenience method that wraps the text in a proper message
        structure and calls ``converse_stream``. Perfect for streaming
        text-only conversations with real-time output.

        Args:
            message: The text message to send
            converse_kwargs: Optional configuration to override session defaults

        Returns:
            ConverseStreamResponse: Enhanced streaming response object

        Example::

            session = ChatSession(client=client, converse_kwargs=ConverseKwargs(
                model_id="anthropic.claude-3-sonnet-20240229-v1:0"
            ))

            # Stream the response
            response = session.converse_text_stream("Write a poem about AI")

            # Print text as it streams
            for text_chunk in session.iterate_text(response):
                print(text_chunk, end="", flush=True)
            print()  # New line after streaming

            # Continue conversation (history includes streamed response)
            response2 = session.converse_text("Make it shorter")
            print(response2.text)
        """
        content_builder = MessageContentBuilder()
        content_builder.add_text(message)
        return self.converse_stream(
            messages=[content_builder.to_message()],
            converse_kwargs=converse_kwargs,
        )

    def collect_message(self, response: "ConverseStreamResponse"):
        """
        Collect the complete message from a streaming response and add to history.

        This method is automatically called by ``iterate_events`` and ``iterate_text``
        after the stream is fully consumed. It ensures the assistant's message is
        added to the conversation history exactly once.

        Args:
            response: The streaming response to collect from

        Note:
            You typically don't need to call this method directly. Use ``iterate_events``
            or ``iterate_text`` instead, which handle collection automatically.
        """
        if response.is_message_collected() is False:
            self._messages.append(response.message)
            object.__setattr__(response, "_message_collected", True)

    def iterate_events(
        self,
        response: "ConverseStreamResponse",
    ) -> T.Generator["ConverseStreamOutput", None, None]:
        """
        Iterate over all streaming events and automatically collect the message.

        This is the recommended way to consume streaming responses in a chat session.
        After all events are yielded, the method automatically adds the complete
        assistant message to the conversation history.

        Args:
            response: The streaming response from ``converse_stream`` or
                ``converse_text_stream``

        Yields:
            ConverseStreamOutput: Enhanced event objects with helper methods

        Example::

            response = session.converse_text_stream("Tell me about Python")

            # Process all events
            for event in session.iterate_events(response):
                if event.is_messageStart():
                    print("Message starting...")
                elif event.is_contentBlockDelta():
                    if event.text:
                        print(event.text, end="", flush=True)
                elif event.is_messageStop():
                    print(f"\\nDone. Stop reason: {event.messageStop.stopReason}")

            # Message is now in history - continue conversation
            response2 = session.converse_text("Tell me more")
        """
        yield from response.iterate_events()
        self.collect_message(response)

    def iterate_text(
        self,
        response: "ConverseStreamResponse",
    ) -> T.Generator[str, None, None]:
        """
        Iterate over text content only and automatically collect the message.

        This is the simplest way to consume streaming text responses in a chat
        session. After all text chunks are yielded, the method automatically adds
        the complete assistant message to the conversation history.

        Args:
            response: The streaming response from ``converse_stream`` or
                ``converse_text_stream``

        Yields:
            str: Text chunks from contentBlockDelta events

        Example::

            response = session.converse_text_stream("Write a haiku")

            # Stream text to console
            for text_chunk in session.iterate_text(response):
                print(text_chunk, end="", flush=True)
            print()  # New line

            # Or collect all text
            response2 = session.converse_text_stream("Write another")
            full_text = "".join(session.iterate_text(response2))
            print(full_text)

            # Both messages are now in history
        """
        yield from response.iterate_text()
        self.collect_message(response)
