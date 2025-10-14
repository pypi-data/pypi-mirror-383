# -*- coding: utf-8 -*-

"""
This module provides an improved interface for the AWS Bedrock Runtime
`converse <https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-runtime/client/converse.html>`_
API. It extends the base boto3 response types and provides a builder pattern for
constructing complex message content.

Key Features:

1. **Enhanced Response Handling**: Convenient text extraction from response messages
2. **Builder Pattern**: Fluent API for constructing message content with multiple types
3. **Type Safety**: Full type hints for all content types (text, images, documents, video, tools)
4. **Flexible Content Sources**: Support for bytes, S3 URIs, and structured content

The main components:

- ``ConverseResponse``: Enhanced response wrapper with convenient text extraction
- ``MessageContentBuilder``: Fluent builder for constructing multi-modal message content
"""

import typing as T
import dataclasses
from functools import cached_property

from func_args.api import BaseFrozenModel, OPT, remove_optional, T_KWARGS
import boto3_dataclass_bedrock_runtime.type_defs

if T.TYPE_CHECKING:  # pragma: no cover
    from mypy_boto3_bedrock_runtime.literals import (
        ConversationRoleType,
        ImageFormatType,
        DocumentFormatType,
        VideoFormatType,
    )
    from mypy_boto3_bedrock_runtime.type_defs import (
        ContentBlockUnionTypeDef,
        MessageUnionTypeDef,
        SystemContentBlockTypeDef,
        InferenceConfigurationTypeDef,
        ToolConfigurationTypeDef,
        GuardrailConfigurationTypeDef,
        PromptVariableValuesTypeDef,
        PerformanceConfigurationTypeDef,
    )


@dataclasses.dataclass(frozen=True)
class ConverseKwargs(BaseFrozenModel):
    """
    Ref:

    - `converse <https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-runtime/client/converse.html>`_
    """

    # fmt: off
    model_id: str = dataclasses.field(default=OPT)
    system: T.Sequence["SystemContentBlockTypeDef"] = dataclasses.field(default=OPT)
    inference_config: "InferenceConfigurationTypeDef" = dataclasses.field(default=OPT)
    tool_config: "ToolConfigurationTypeDef" = dataclasses.field(default=OPT)
    guardrail_config: "GuardrailConfigurationTypeDef" = dataclasses.field(default=OPT)
    additional_model_request_fields: T.Mapping[str, T.Any] = dataclasses.field(default=OPT)
    prompt_variables: T.Mapping[str, "PromptVariableValuesTypeDef"] = dataclasses.field(default=OPT)
    additional_model_response_field_paths: T.Sequence[str] = dataclasses.field(default=OPT)
    request_metadata: T.Mapping[str, str] = dataclasses.field(default=OPT)
    performance_config: "PerformanceConfigurationTypeDef" = dataclasses.field(default=OPT)
    # fmt: on

    def to_boto3_kwargs(self) -> T_KWARGS:
        return remove_optional(
            modelId=self.model_id,
            system=self.system,
            inferenceConfig=self.inference_config,
            toolConfig=self.tool_config,
            guardrailConfig=self.guardrail_config,
            additionalModelRequestFields=self.additional_model_request_fields,
            promptVariables=self.prompt_variables,
            additionalModelResponseFieldPaths=self.additional_model_response_field_paths,
            requestMetadata=self.request_metadata,
            performanceConfig=self.performance_config,
        )


@dataclasses.dataclass(frozen=True)
class ConverseResponse(
    boto3_dataclass_bedrock_runtime.type_defs.ConverseResponse,
):
    """
    Enhanced wrapper for Bedrock converse API response.

    This class extends the base ``ConverseResponse`` type from boto3_dataclass with
    convenient helper properties for extracting common response data.

    The AWS Bedrock converse API returns a complex nested structure containing:
    - Response metadata (request ID, usage stats)
    - Output message with content blocks
    - Stop reason and additional metadata

    This wrapper simplifies access to the most commonly needed data, particularly
    text content from the model's response.

    Attributes:
        text: Convenient access to the first text content block, or None if not available

    Example::

        import boto3
        from aws_bedrock_runtime_mate.converse import ConverseResponse

        client = boto3.client("bedrock-runtime")
        response = client.converse(
            modelId="anthropic.claude-3-sonnet-20240229-v1:0",
            messages=[{"role": "user", "content": [{"text": "Hello"}]}],
        )

        # Wrap the response
        converse_response = ConverseResponse(boto3_raw_data=response)

        # Easy text extraction
        print(converse_response.text)  # "Hello! How can I help you today?"

        # Access full response data
        print(converse_response.stopReason)
        print(converse_response.usage.inputTokens)
    """

    @cached_property
    def text(self) -> str | None:
        """
        Extract the text content from the first content block in the response.

        This is a convenience property that safely extracts the text from the first
        content block of the model's output message. It handles the complex nested
        structure of the AWS response automatically.

        Returns:
            str | None: The text content from the first content block, or None if:
                - The response doesn't contain any content blocks
                - The first content block is not a text block (e.g., tool use, image)
                - An error occurs during extraction

        Example::

            response = client.converse(
                modelId="anthropic.claude-3-sonnet-20240229-v1:0",
                messages=[{"role": "user", "content": [{"text": "Hello"}]}],
            )
            converse_response = ConverseResponse(boto3_raw_data=response)

            # Simple text extraction
            if converse_response.text:
                print(converse_response.text)
            else:
                print("No text content in response")
        """
        try:
            return self.output.message.content[0].text
        except Exception:
            return None


@dataclasses.dataclass
class MessageContentBuilder:
    """
    Fluent builder for constructing multi-modal message content for Bedrock conversations.

    This class provides a convenient, type-safe way to construct complex message content
    that may include multiple types of content blocks:

    - Text content
    - Images (from bytes or S3)
    - Documents (from bytes, text, structured content, or S3)
    - Videos (from bytes or S3)
    - Tool use and tool results
    - Cache points for prompt caching
    - Guard content (not yet implemented)
    - Reasoning content (not yet implemented)
    - Citations content (not yet implemented)

    The builder follows a fluent interface pattern, allowing method chaining for
    constructing complex messages in a readable way.

    Example::

        from aws_bedrock_runtime_mate.converse import MessageContentBuilder

        # Simple text message
        builder = MessageContentBuilder()
        builder.add_text("Hello, Claude!")
        message = builder.to_message()

        # Multi-modal message with text and image
        builder = MessageContentBuilder()
        builder.add_text("What's in this image?")
        builder.add_image(format="png", bytes=image_bytes)
        message = builder.to_message(role="user")

        # Chained construction
        message = (
            MessageContentBuilder()
                .add_text("Analyze this document")
                .add_document(name="report.pdf", format="pdf", bytes=pdf_bytes)
                .to_message()
        )

        # Tool result message
        builder = MessageContentBuilder()
        builder.add_tool_result(
            tool_use_id="tool_123",
            content=[{"text": "The weather is sunny"}]
        )
        message = builder.to_message(role="user")
    """

    _content_blocks: list["ContentBlockUnionTypeDef"] = dataclasses.field(init=False)

    def __post_init__(self):
        self._content_blocks = []

    def to_message(
        self,
        role: "ConversationRoleType" = "user",
    ) -> "MessageUnionTypeDef":
        """
        Convert the built content blocks into a message dictionary.

        Args:
            role: The role of the message sender. Defaults to "user".
                Valid values are "user" or "assistant".

        Returns:
            MessageUnionTypeDef: A message dictionary compatible with the Bedrock
                converse API, containing the role and content blocks.

        Example::

            builder = MessageContentBuilder()
            builder.add_text("Hello!")

            # User message (default)
            user_msg = builder.to_message()

            # Assistant message
            assistant_msg = builder.to_message(role="assistant")
        """
        return {"role": role, "content": self._content_blocks}

    def _add_content_block(self, block: "ContentBlockUnionTypeDef"):
        """
        Internal helper to add a content block and return self for chaining.

        Args:
            block: The content block to add

        Returns:
            MessageContentBuilder: Self for method chaining
        """
        self._content_blocks.append(block)
        return self

    def add_text(self, text: str):
        """
        Add a text content block to the message.

        Args:
            text: The text content to add

        Returns:
            MessageContentBuilder: Self for method chaining

        Example::

            builder = MessageContentBuilder()
            builder.add_text("Hello, how can I help you?")
            builder.add_text("I can answer questions about many topics.")
        """
        block = {
            "text": text,
        }
        return self._add_content_block(block)

    def add_image(
        self,
        format: "ImageFormatType",
        bytes: bytes = OPT,
        s3_uri: str = OPT,
        s3_bucket_owner: str = OPT,
    ):
        """
        Add an image content block to the message.

        Images can be provided either as raw bytes or as an S3 URI. Exactly one
        source must be specified.

        Args:
            format: The image format (e.g., "png", "jpeg", "gif", "webp")
            bytes: Raw image bytes (mutually exclusive with S3 parameters)
            s3_uri: S3 URI to the image (e.g., "s3://bucket/key.png")
            s3_bucket_owner: AWS account ID of the S3 bucket owner (optional)

        Returns:
            MessageContentBuilder: Self for method chaining

        Example::

            # From bytes
            with open("image.png", "rb") as f:
                image_bytes = f.read()
            builder = MessageContentBuilder()
            builder.add_text("What's in this image?")
            builder.add_image(format="png", bytes=image_bytes)

            # From S3
            builder = MessageContentBuilder()
            builder.add_image(format="jpeg", s3_uri="s3://my-bucket/photo.jpg")
        """
        block = {"format": format}
        if bytes is not OPT:
            block["source"] = {"bytes": bytes}
        else:
            s3_location = remove_optional(uri=s3_uri, bucketOwner=s3_bucket_owner)
            block["source"] = {"s3Location": s3_location}
        return self._add_content_block(block)

    def add_document(
        self,
        name: str,
        format: "DocumentFormatType" = OPT,
        bytes: bytes = OPT,
        text: str = OPT,
        content: T.Sequence["ContentBlockUnionTypeDef"] = OPT,
        s3_uri: str = OPT,
        s3_bucket_owner: str = OPT,
    ):
        """
        Add a document content block to the message.

        Documents can be provided in multiple ways: raw bytes, plain text, structured
        content blocks, or as an S3 URI. Exactly one source must be specified.

        Args:
            name: Document name (e.g., "report.pdf", "data.csv")
            format: Document format (e.g., "pdf", "csv", "doc", "xls", "html", "txt", "md")
            bytes: Raw document bytes
            text: Plain text content of the document
            content: Structured content blocks (for complex documents)
            s3_uri: S3 URI to the document
            s3_bucket_owner: AWS account ID of the S3 bucket owner (optional)

        Returns:
            MessageContentBuilder: Self for method chaining

        Example::

            # From bytes
            with open("report.pdf", "rb") as f:
                pdf_bytes = f.read()
            builder = MessageContentBuilder()
            builder.add_text("Summarize this report")
            builder.add_document(name="report.pdf", format="pdf", bytes=pdf_bytes)

            # From text
            builder = MessageContentBuilder()
            builder.add_document(
                name="notes.txt",
                format="txt",
                text="Meeting notes: Discussed Q4 goals..."
            )

            # From S3
            builder = MessageContentBuilder()
            builder.add_document(
                name="data.csv",
                format="csv",
                s3_uri="s3://my-bucket/data.csv"
            )
        """
        block = {
            "name": name,
            "format": format,
        }
        if bytes is not OPT:
            block["source"] = {"bytes": bytes}
        elif text is not OPT:
            block["source"] = {"text": text}
        elif content is not OPT:
            block["source"] = {"content": content}
        else:
            s3_location = remove_optional(uri=s3_uri, bucketOwner=s3_bucket_owner)
            block["source"] = {"s3Location": s3_location}
        block = remove_optional(**block)
        return self._add_content_block(block)

    def add_video(
        self,
        format: "VideoFormatType",
        bytes: bytes = OPT,
        s3_uri: str = OPT,
        s3_bucket_owner: str = OPT,
    ):
        """
        Add a video content block to the message.

        Videos can be provided either as raw bytes or as an S3 URI. Exactly one
        source must be specified.

        Args:
            format: The video format (e.g., "mp4", "mov", "avi", "mkv", "webm")
            bytes: Raw video bytes (mutually exclusive with S3 parameters)
            s3_uri: S3 URI to the video (e.g., "s3://bucket/video.mp4")
            s3_bucket_owner: AWS account ID of the S3 bucket owner (optional)

        Returns:
            MessageContentBuilder: Self for method chaining

        Example::

            # From bytes
            with open("demo.mp4", "rb") as f:
                video_bytes = f.read()
            builder = MessageContentBuilder()
            builder.add_text("Describe what happens in this video")
            builder.add_video(format="mp4", bytes=video_bytes)

            # From S3
            builder = MessageContentBuilder()
            builder.add_video(format="mp4", s3_uri="s3://my-bucket/presentation.mp4")
        """
        block = {"format": format}
        if bytes is not OPT:
            block["source"] = {"bytes": bytes}
        else:
            s3_location = remove_optional(uri=s3_uri, bucketOwner=s3_bucket_owner)
            block["source"] = {"s3Location": s3_location}
        return self._add_content_block(block)

    def add_tool_use(
        self,
        tool_use_id: str,
        name: str,
        input: T.Any,
    ):
        """
        Add a tool use content block to the message.

        This is typically used in assistant messages to indicate that the model
        wants to call a tool (function). The user then executes the tool and
        responds with a tool result.

        Args:
            tool_use_id: Unique identifier for this tool use (generated by the model)
            name: Name of the tool to use
            input: Input parameters for the tool (typically a dictionary)

        Returns:
            MessageContentBuilder: Self for method chaining

        Example::

            # Assistant message with tool use (typically from model response)
            builder = MessageContentBuilder()
            builder.add_tool_use(
                tool_use_id="tool_abc123",
                name="get_weather",
                input={"location": "San Francisco", "unit": "celsius"}
            )
            assistant_msg = builder.to_message(role="assistant")
        """
        block = {
            "toolUse": {
                "toolUseId": tool_use_id,
                "name": name,
                "input": input,
            }
        }
        return self._add_content_block(block)

    def add_tool_result(
        self,
        tool_use_id: str,
        content: T.Sequence["ContentBlockUnionTypeDef"],
    ):
        """
        Add a tool result content block to the message.

        This is used in user messages to provide the results of a tool execution
        after the model has requested a tool use.

        Args:
            tool_use_id: The tool use ID from the model's tool use request
            content: Content blocks containing the tool result (typically text)

        Returns:
            MessageContentBuilder: Self for method chaining

        Example::

            # User message with tool result
            builder = MessageContentBuilder()
            builder.add_tool_result(
                tool_use_id="tool_abc123",
                content=[{"text": "The weather in San Francisco is 18°C and sunny"}]
            )
            user_msg = builder.to_message(role="user")

        Note:
            This follows the tool calling pattern:
            1. User sends initial request
            2. Assistant responds with tool_use
            3. User executes tool and responds with tool_result
            4. Assistant provides final answer
        """
        block = {
            "toolResult": {
                "toolUseId": tool_use_id,
                "content": content,
            }
        }
        return self._add_content_block(block)

    def add_guard_content(
        self,
    ):
        """
        Add guard content to the message.

        Note:
            This feature is not yet implemented. Guard content is used for
            content filtering and safety guardrails.

        Raises:
            NotImplementedError: This method is not yet implemented
        """
        raise NotImplementedError

    def add_cache_point(self, type: str = "default"):
        """
        Add a cache point marker to enable prompt caching.

        Cache points allow you to mark content that should be cached for reuse
        in subsequent requests, reducing latency and costs. Content before a
        cache point can be reused in future conversations.

        Args:
            type: The cache point type. Defaults to "default".

        Returns:
            MessageContentBuilder: Self for method chaining

        Example::

            # Cache system instructions for reuse
            builder = MessageContentBuilder()
            builder.add_text("You are a helpful coding assistant...")
            builder.add_cache_point()  # Cache everything before this point
            builder.add_text("Now help me with this specific code...")
            message = builder.to_message()

        Note:
            Prompt caching can significantly reduce costs and latency for
            conversations with large amounts of repeated context like:
            - System instructions
            - Large documents
            - Code repositories
            - API documentation

            Refer to the Bedrock documentation for model-specific caching
            capabilities and pricing.
        """
        block = {"cachePoint": {"type": type}}
        return self._add_content_block(block)

    def add_reasoning_content(
        self,
    ):
        """
        Add reasoning content to the message.

        Note:
            This feature is not yet implemented. Reasoning content is used
            with models that support extended thinking and can return their
            reasoning process.

        Raises:
            NotImplementedError: This method is not yet implemented
        """
        raise NotImplementedError

    def add_citations_content(
        self,
    ):
        """
        Add citations content to the message.

        Note:
            This feature is not yet implemented. Citations content is used
            with models that can provide source citations for their responses.

        Raises:
            NotImplementedError: This method is not yet implemented
        """
        raise NotImplementedError
