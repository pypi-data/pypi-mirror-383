# -*- coding: utf-8 -*-

"""
This module provides an improved interface for the AWS Bedrock Runtime
`converse_stream <https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-runtime/client/converse_stream.html>`_
API.

The main improvements over the raw AWS API include:

1. **Type-safe event checking**: Boolean methods to identify event types
2. **Convenient text extraction**: Automatic extraction of text from content blocks
3. **Stream management**: Automatic caching of consumed streams for replay
4. **Simplified iteration**: Generator methods for both events and text content
"""

import typing as T
import dataclasses
from functools import cached_property

import boto3_dataclass_bedrock_runtime.type_defs

if T.TYPE_CHECKING:  # pragma: no cover
    from mypy_boto3_bedrock_runtime.type_defs import MessageUnionTypeDef


class InternalServerException(Exception):
    pass


class ModelStreamErrorException(Exception):
    pass


class ValidationException(Exception):
    pass


class ThrottlingException(Exception):
    pass


class ServiceUnavailableException(Exception):
    pass


@dataclasses.dataclass(frozen=True)
class ConverseStreamOutput(
    boto3_dataclass_bedrock_runtime.type_defs.ConverseStreamOutput,
):
    """
    Enhanced wrapper for individual streaming output events from Bedrock ``converse_stream``.

    This class extends the base ``ConverseStreamOutput`` type from boto3_dataclass with
    convenient helper methods for:

    - Identifying the type of streaming event (messageStart, contentBlockDelta, etc.)
    - Extracting text content from content block deltas
    - Extracting reasoning content from content block deltas (for models that support it)

    The Bedrock converse_stream API emits different event types during the streaming
    response lifecycle:

    - ``messageStart``: Indicates the beginning of a message
    - ``contentBlockStart``: Indicates the beginning of a content block
    - ``contentBlockDelta``: Contains incremental content (text, reasoning, etc.)
    - ``contentBlockStop``: Indicates the end of a content block
    - ``messageStop``: Indicates the end of the message

    Attributes:
        text: The text content from a contentBlockDelta event, or None if not applicable
        reasoning_content_text: The reasoning content text from a contentBlockDelta event,
            or None if not applicable (only available on models with reasoning capabilities)
    """

    def is_messageStart(self) -> bool:
        """
        Check if this event represents the start of a message.

        Returns:
            bool: True if this is a messageStart event, False otherwise.
        """
        return "messageStart" in self.boto3_raw_data

    def is_contentBlockStart(self) -> bool:
        """
        Check if this event represents the start of a content block.

        Returns:
            bool: True if this is a contentBlockStart event, False otherwise.
        """
        return "contentBlockStart" in self.boto3_raw_data

    def is_contentBlockDelta(self) -> bool:
        """
        Check if this event contains incremental content (delta).

        This is the most common event type during streaming, containing
        actual content chunks like text or reasoning content.

        Returns:
            bool: True if this is a contentBlockDelta event, False otherwise.
        """
        return "contentBlockDelta" in self.boto3_raw_data

    def is_contentBlockStop(self) -> bool:
        """
        Check if this event represents the end of a content block.

        Returns:
            bool: True if this is a contentBlockStop event, False otherwise.
        """
        return "contentBlockStop" in self.boto3_raw_data

    def is_messageStop(self) -> bool:
        """
        Check if this event represents the end of the message.

        This event typically includes metadata like stop reason and token usage.

        Returns:
            bool: True if this is a messageStop event, False otherwise.
        """
        return "messageStop" in self.boto3_raw_data

    @cached_property
    def text(self) -> str | None:
        """
        Extract text content from a contentBlockDelta event.

        This property provides convenient access to the text content within
        a streaming delta event. It automatically handles the nested structure
        of the AWS response and returns None if:

        - This is not a contentBlockDelta event
        - The delta doesn't contain text content
        - The content structure is different (e.g., image, tool use)

        Returns:
            str | None: The text content chunk, or None if not applicable.
        """
        if self.is_contentBlockDelta():
            try:
                return self.contentBlockDelta.delta.text
            except:
                return None
        else:
            return None

    @cached_property
    def reasoning_content_text(self) -> str | None:
        """
        Extract reasoning content text from a contentBlockDelta event.

        Some advanced Bedrock models (like Claude with extended thinking)
        can return reasoning content that shows the model's thought process.
        This property provides convenient access to that reasoning text.

        Returns:
            str | None: The reasoning content text chunk, or None if:
                - This is not a contentBlockDelta event
                - The model doesn't support reasoning content
                - The delta doesn't contain reasoning content
        """
        if self.is_contentBlockDelta():
            try:
                return self.contentBlockDelta.delta.reasoningContent.text
            except:
                return None
        else:
            return None

    def is_exception(self) -> bool:
        return (
            ("internalServerException" in self.boto3_raw_data)
            or ("modelStreamErrorException" in self.boto3_raw_data)
            or ("validationException" in self.boto3_raw_data)
            or ("throttlingException" in self.boto3_raw_data)
            or ("serviceUnavailableException" in self.boto3_raw_data)
        )

    def raise_for_exception(self):
        if "internalServerException" in self.boto3_raw_data:
            raise InternalServerException(self.internalServerException.message)
        if "modelStreamErrorException" in self.boto3_raw_data:
            raise ModelStreamErrorException(self.modelStreamErrorException.message)
        if "validationException" in self.boto3_raw_data:
            raise ValidationException(self.validationException.message)
        if "throttlingException" in self.boto3_raw_data:
            raise ThrottlingException(self.throttlingException.message)
        if "serviceUnavailableException" in self.boto3_raw_data:
            raise ServiceUnavailableException(self.serviceUnavailableException.message)


@dataclasses.dataclass(frozen=True)
class ConverseStreamResponse(
    boto3_dataclass_bedrock_runtime.type_defs.ConverseStreamResponse
):
    """
    Enhanced wrapper for the streaming response from Bedrock converse_stream API.

    This class extends the base ``ConverseStreamResponse`` type with intelligent
    stream management capabilities:

    - **Stream caching**: Automatically caches events as they are consumed, allowing
      multiple iterations over the same response
    - **Event iteration**: Provides a generator for iterating over all streaming events
    - **Text-only iteration**: Convenient generator for extracting just the text content

    The AWS Bedrock streaming API returns an event stream that can only be consumed once.
    This wrapper solves that limitation by caching events internally, enabling:

    1. Multiple iterations over the same response
    2. Safe inspection after initial consumption
    3. Simplified text extraction without manual event filtering

    Attributes:
        _streams: Internal cache of consumed streaming events
        _stream_consumed: Flag indicating whether the stream has been fully consumed

    Example::

        import boto3
        from aws_bedrock_runtime_mate.converse_stream import ConverseStreamResponse

        client = boto3.client("bedrock-runtime")
        response = client.converse_stream(
            modelId="anthropic.claude-3-sonnet-20240229-v1:0",
            messages=[{"role": "user", "content": [{"text": "Tell me a story"}]}],
        )

        # Wrap the response
        stream_response = ConverseStreamResponse(boto3_raw_data=response)

        # First iteration - consumes the stream and caches events
        full_text = ""
        for text_chunk in stream_response.iterate_text():
            full_text += text_chunk
            print(text_chunk, end="", flush=True)

        # Second iteration - replays cached events (no API call)
        for event in stream_response.iterate_events():
            if event.is_messageStop():
                print(f"\\nStop reason: {event.messageStop.stopReason}")
    """

    _streams: list["ConverseStreamOutput"] = dataclasses.field(default_factory=list)
    _stream_consumed: bool = dataclasses.field(default=False)
    _message_collected: bool = dataclasses.field(default=False)
    _message: T.Optional["MessageUnionTypeDef"] = dataclasses.field(default=None)
    _text: str | None = dataclasses.field(default=None)

    def is_stream_consumed(self) -> bool:
        """
        Check if the streaming response has been fully consumed.

        Once a stream is consumed, subsequent iterations will use cached events
        instead of attempting to read from the original stream.

        Returns:
            bool: True if the stream has been consumed, False otherwise.

        Example::

            stream_response = ConverseStreamResponse(boto3_raw_data=response)
            print(stream_response.is_stream_consumed())  # False

            # Consume the stream
            for event in stream_response.iterate_events():
                pass

            print(stream_response.is_stream_consumed())  # True
        """
        return self._stream_consumed

    def is_message_collected(self) -> bool:
        """
        Check if the message has been collected by multi round converse.

        Returns:
            bool: True if the message has been collected, False otherwise.
        """
        return self._message_collected

    def iterate_events(self) -> T.Generator[
        "ConverseStreamOutput",
        None,
        None,
    ]:
        """
        Iterate over all streaming events with automatic caching.

        This method provides a generator that yields ``ConverseStreamOutput`` objects
        for each event in the stream. Key features:

        - **First iteration**: Consumes the AWS stream, wraps each event in
          ``ConverseStreamOutput``, caches it, and yields it
        - **Subsequent iterations**: Yields cached events without making additional API calls
        - **Thread-safe caching**: Events are stored as they are consumed

        The generator yields events in the order they were received:

        1. messageStart - Initial message metadata
        2. contentBlockStart - Beginning of content block(s)
        3. contentBlockDelta - Incremental content chunks (text, reasoning, etc.)
        4. contentBlockStop - End of content block(s)
        5. messageStop - Final message metadata (stop reason, usage stats)

        Yields:
            ConverseStreamOutput: Enhanced event objects with helper methods

        Note:
            TODO: Currently, this method collects all event types. Future versions may add
            filtering capabilities for specific content types (images, documents, video).

        Example::

            stream_response = ConverseStreamResponse(boto3_raw_data=response)

            # Process all events
            for event in stream_response.iterate_events():
                if event.is_messageStart():
                    print("Message starting...")
                elif event.is_contentBlockDelta():
                    if event.text:
                        print(event.text, end="", flush=True)
                elif event.is_messageStop():
                    print(f"\\nFinished: {event.messageStop.stopReason}")

            # Iterate again (uses cached events)
            for event in stream_response.iterate_events():
                print(f"Event type: {type(event)}")
        """
        # Important, the stream can be consumed only once
        if self._stream_consumed:
            for event in self._streams:
                yield event
        else:
            for event in self.stream:
                event = ConverseStreamOutput(boto3_raw_data=event)
                event.raise_for_exception()  # Raise if this event is an exception
                self._streams.append(event)
                yield event
            object.__setattr__(self, "_stream_consumed", True)

    def iterate_text(self) -> T.Generator[str, None, None]:
        """
        Iterate over text content only, filtering out non-text events.

        This is a convenience method that wraps ``iterate_events()`` and yields
        only the text content from contentBlockDelta events. It automatically:

        - Filters out non-delta events (messageStart, messageStop, etc.)
        - Extracts text content from delta events
        - Skips events with no text content (e.g., tool use, images)

        This is the simplest way to collect or stream text responses from
        Bedrock models.

        Yields:
            str: Text chunks from contentBlockDelta events

        Example::

            stream_response = ConverseStreamResponse(boto3_raw_data=response)

            # Stream text to console
            for text_chunk in stream_response.iterate_text():
                print(text_chunk, end="", flush=True)

            # Or collect all text
            full_text = "".join(stream_response.iterate_text())
            print(full_text)
        """
        for event in self.iterate_events():
            if event.text:
                yield event.text

    @cached_property
    def message(self) -> "MessageUnionTypeDef":
        """
        Note:
            TODO: Currently, this method collects all event types. Future versions may add
            filtering capabilities for specific content types (images, documents, video).
        """
        if self._message is None:
            message = {}
            content = []
            text_chunks = []
            # 每次都是
            for event in self.iterate_events():
                if event.is_messageStart():
                    message["role"] = event.messageStart.role
                elif event.is_contentBlockDelta():
                    if event.text:
                        text_chunks.append(event.text)
                else:  # TODO, college all other event types
                    pass
            if text_chunks:
                text = "".join(text_chunks)
                content.append({"text": "".join(text_chunks)})
                object.__setattr__(self, "_text", text)
            message["content"] = content
            object.__setattr__(self, "_message", message)
        return self._message

    @cached_property
    def text(self) -> str:
        if self._text is None:
            _ = self.message
        return self._text
