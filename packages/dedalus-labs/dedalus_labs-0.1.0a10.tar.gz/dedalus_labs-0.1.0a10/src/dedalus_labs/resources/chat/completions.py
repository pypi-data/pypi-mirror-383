# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Union, Iterable, Optional
from typing_extensions import Literal, overload

import httpx

from ..._types import Body, Omit, Query, Headers, NotGiven, SequenceNotStr, omit, not_given
from ..._utils import required_args, maybe_transform, async_maybe_transform
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ..._streaming import Stream, AsyncStream
from ...types.chat import completion_create_params
from ..._base_client import make_request_options
from ...types.chat.stream_chunk import StreamChunk

__all__ = ["CompletionsResource", "AsyncCompletionsResource"]


class CompletionsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> CompletionsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/dedalus-labs/dedalus-sdk-python#accessing-raw-response-data-eg-headers
        """
        return CompletionsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> CompletionsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/dedalus-labs/dedalus-sdk-python#with_streaming_response
        """
        return CompletionsResourceWithStreamingResponse(self)

    @overload
    def create(
        self,
        *,
        messages: Union[Iterable[Dict[str, object]], str],
        model: completion_create_params.Model,
        agent_attributes: Optional[Dict[str, float]] | Omit = omit,
        audio: Optional[Dict[str, object]] | Omit = omit,
        disable_automatic_function_calling: Optional[bool] | Omit = omit,
        frequency_penalty: Optional[float] | Omit = omit,
        function_call: Union[str, Dict[str, object], None] | Omit = omit,
        functions: Optional[Iterable[Dict[str, object]]] | Omit = omit,
        generation_config: Optional[Dict[str, object]] | Omit = omit,
        guardrails: Optional[Iterable[Dict[str, object]]] | Omit = omit,
        handoff_config: Optional[Dict[str, object]] | Omit = omit,
        input: Union[Iterable[Dict[str, object]], str, None] | Omit = omit,
        instructions: Union[str, Iterable[Dict[str, object]], None] | Omit = omit,
        logit_bias: Optional[Dict[str, int]] | Omit = omit,
        logprobs: Optional[bool] | Omit = omit,
        max_completion_tokens: Optional[int] | Omit = omit,
        max_tokens: Optional[int] | Omit = omit,
        max_turns: Optional[int] | Omit = omit,
        mcp_servers: Optional[completion_create_params.MCPServers] | Omit = omit,
        metadata: Optional[Dict[str, str]] | Omit = omit,
        modalities: Optional[SequenceNotStr[str]] | Omit = omit,
        model_attributes: Optional[Dict[str, Dict[str, float]]] | Omit = omit,
        n: Optional[int] | Omit = omit,
        parallel_tool_calls: Optional[bool] | Omit = omit,
        prediction: Optional[Dict[str, object]] | Omit = omit,
        presence_penalty: Optional[float] | Omit = omit,
        prompt_cache_key: Optional[str] | Omit = omit,
        reasoning_effort: Optional[Literal["low", "medium", "high"]] | Omit = omit,
        response_format: Optional[Dict[str, object]] | Omit = omit,
        safety_identifier: Optional[str] | Omit = omit,
        safety_settings: Optional[Iterable[Dict[str, object]]] | Omit = omit,
        seed: Optional[int] | Omit = omit,
        service_tier: Optional[Literal["auto", "default"]] | Omit = omit,
        stop: Optional[SequenceNotStr[str]] | Omit = omit,
        store: Optional[bool] | Omit = omit,
        stream: Literal[False] | Omit = omit,
        stream_options: Optional[Dict[str, object]] | Omit = omit,
        system: Union[str, Iterable[Dict[str, object]], None] | Omit = omit,
        temperature: Optional[float] | Omit = omit,
        thinking: Optional[completion_create_params.Thinking] | Omit = omit,
        tool_choice: Union[str, Dict[str, object], None] | Omit = omit,
        tool_config: Optional[Dict[str, object]] | Omit = omit,
        tools: Optional[Iterable[Dict[str, object]]] | Omit = omit,
        top_k: Optional[int] | Omit = omit,
        top_logprobs: Optional[int] | Omit = omit,
        top_p: Optional[float] | Omit = omit,
        user: Optional[str] | Omit = omit,
        verbosity: Optional[Literal["low", "medium", "high"]] | Omit = omit,
        web_search_options: Optional[Dict[str, object]] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
        idempotency_key: str | None = None,
    ) -> StreamChunk:
        """
        Create a chat completion.

        This endpoint provides a vendor-agnostic chat completions API that works with
        thousands of LLMs. It supports MCP integration, multi-model routing with
        intelligent agentic handoffs, client-side and server-side tool execution, and
        streaming and non-streaming responses.

        Args: request: Chat completion request with messages, model, and configuration.
        http_request: FastAPI request object for accessing headers and state.
        background_tasks: FastAPI background tasks for async billing operations. user:
        Authenticated user with validated API key and sufficient balance.

        Returns: ChatCompletion: OpenAI-compatible completion response with usage data.

        Raises: HTTPException: - 401 if authentication fails or insufficient balance. -
        400 if request validation fails. - 500 if internal processing error occurs.

        Billing: - Token usage billed automatically based on model pricing - MCP tool
        calls billed separately using credits system - Streaming responses billed after
        completion via background task

        Example: Basic chat completion: ```python from dedalus_labs import Dedalus

            client = Dedalus(api_key="your-api-key")

            completion = client.chat.completions.create(
                model="openai/gpt-5",
                messages=[{"role": "user", "content": "Hello, how are you?"}],
            )

            print(completion.choices[0].message.content)
            ```

            With tools and MCP servers:
            ```python
            completion = client.chat.completions.create(
                model="openai/gpt-5",
                messages=[{"role": "user", "content": "Search for recent AI news"}],
                tools=[
                    {
                        "type": "function",
                        "function": {
                            "name": "search_web",
                            "description": "Search the web for information",
                        },
                    }
                ],
                mcp_servers=["dedalus-labs/brave-search"],
            )
            ```

            Multi-model routing:
            ```python
            completion = client.chat.completions.create(
                model=[
                    "openai/gpt-4o-mini",
                    "openai/gpt-5",
                    "anthropic/claude-sonnet-4-20250514",
                ],
                messages=[{"role": "user", "content": "Analyze this complex data"}],
                agent_attributes={"complexity": 0.8, "accuracy": 0.9},
            )
            ```

            Streaming response:
            ```python
            stream = client.chat.completions.create(
                model="openai/gpt-5",
                messages=[{"role": "user", "content": "Tell me a story"}],
                stream=True,
            )

            for chunk in stream:
                if chunk.choices[0].delta.content:
                    print(chunk.choices[0].delta.content, end="")
            ```

        Args:
          messages: Conversation history. Accepts either a list of message objects or a string,
              which is treated as a single user message.

          model: Model(s) to use for completion. Can be a single model ID, a DedalusModel object,
              or a list for multi-model routing. Single model: 'openai/gpt-4',
              'anthropic/claude-3-5-sonnet-20241022', 'openai/gpt-4o-mini', or a DedalusModel
              instance. Multi-model routing: ['openai/gpt-4o-mini', 'openai/gpt-4',
              'anthropic/claude-3-5-sonnet'] or list of DedalusModel objects - agent will
              choose optimal model based on task complexity.

          agent_attributes: Attributes for the agent itself, influencing behavior and model selection.
              Format: {'attribute': value}, where values are 0.0-1.0. Common attributes:
              'complexity', 'accuracy', 'efficiency', 'creativity', 'friendliness'. Higher
              values indicate stronger preference for that characteristic.

          audio: Parameters for audio output. Required when requesting audio responses (for
              example, modalities including 'audio').

          disable_automatic_function_calling: Google-only flag to disable the SDK's automatic function execution. When true,
              the model returns function calls for the client to execute manually.

          frequency_penalty: Number between -2.0 and 2.0. Positive values penalize new tokens based on their
              existing frequency in the text so far, decreasing the model's likelihood to
              repeat the same line verbatim.

          function_call: Deprecated in favor of 'tool_choice'. Controls which function is called by the
              model (none, auto, or specific name).

          functions: Deprecated in favor of 'tools'. Legacy list of function definitions the model
              may generate JSON inputs for.

          generation_config: Google generationConfig object. Merged with auto-generated config. Use for
              Google-specific params (candidateCount, responseMimeType, etc.).

          guardrails: Guardrails to apply to the agent for input/output validation and safety checks.
              Reserved for future use - guardrails configuration format not yet finalized.

          handoff_config: Configuration for multi-model handoffs and agent orchestration. Reserved for
              future use - handoff configuration format not yet finalized.

          input: Convenience alias for Responses-style `input`. Used when `messages` is omitted
              to provide the user prompt directly.

          instructions: Convenience alias for Responses-style `instructions`. Takes precedence over
              `system` and over system-role messages when provided.

          logit_bias: Modify the likelihood of specified tokens appearing in the completion. Accepts a
              JSON object mapping token IDs (as strings) to bias values from -100 to 100. The
              bias is added to the logits before sampling; values between -1 and 1 nudge
              selection probability, while values like -100 or 100 effectively ban or require
              a token.

          logprobs: Whether to return log probabilities of the output tokens. If true, returns the
              log probabilities for each token in the response content.

          max_completion_tokens: An upper bound for the number of tokens that can be generated for a completion,
              including visible output and reasoning tokens.

          max_tokens: The maximum number of tokens that can be generated in the chat completion. This
              value can be used to control costs for text generated via API. This value is now
              deprecated in favor of 'max_completion_tokens' and is not compatible with
              o-series models.

          max_turns: Maximum number of turns for agent execution before terminating (default: 10).
              Each turn represents one model inference cycle. Higher values allow more complex
              reasoning but increase cost and latency.

          mcp_servers: MCP (Model Context Protocol) server addresses to make available for server-side
              tool execution. Entries can be URLs (e.g., 'https://mcp.example.com'), slugs
              (e.g., 'dedalus-labs/brave-search'), or structured objects specifying
              slug/version/url. MCP tools are executed server-side and billed separately.

          metadata: Set of up to 16 key-value string pairs that can be attached to the request for
              structured metadata.

          modalities: Output types you would like the model to generate. Most models default to
              ['text']; some support ['text', 'audio'].

          model_attributes: Attributes for individual models used in routing decisions during multi-model
              execution. Format: {'model_name': {'attribute': value}}, where values are
              0.0-1.0. Common attributes: 'intelligence', 'speed', 'cost', 'creativity',
              'accuracy'. Used by agent to select optimal model based on task requirements.

          n: How many chat completion choices to generate for each input message. Keep 'n' as
              1 to minimize costs.

          parallel_tool_calls: Whether to enable parallel function calling during tool use.

          prediction: Configuration for predicted outputs. Improves response times when you already
              know large portions of the response content.

          presence_penalty: Number between -2.0 and 2.0. Positive values penalize new tokens based on
              whether they appear in the text so far, increasing the model's likelihood to
              talk about new topics.

          prompt_cache_key: Used by OpenAI to cache responses for similar requests and optimize cache hit
              rates. Replaces the legacy 'user' field for caching.

          reasoning_effort: Constrains effort on reasoning for supported reasoning models. Higher values use
              more compute, potentially improving reasoning quality at the cost of latency and
              tokens.

          response_format:
              An object specifying the format that the model must output. Use {'type':
              'json_schema', 'json_schema': {...}} for structured outputs or {'type':
              'json_object'} for the legacy JSON mode. Currently only OpenAI-prefixed models
              honour this field; Anthropic and Google requests will return an
              invalid_request_error if it is supplied.

          safety_identifier: Stable identifier used to help detect users who might violate OpenAI usage
              policies. Consider hashing end-user identifiers before sending.

          safety_settings: Google safety settings (harm categories and thresholds).

          seed: If specified, system will make a best effort to sample deterministically.
              Determinism is not guaranteed for the same seed across different models or API
              versions.

          service_tier: Specifies the processing tier used for the request. 'auto' uses project
              defaults, while 'default' forces standard pricing and performance.

          stop: Not supported with latest reasoning models 'o3' and 'o4-mini'.

                      Up to 4 sequences where the API will stop generating further tokens; the returned text will not contain the stop sequence.

          store: Whether to store the output of this chat completion request for OpenAI model
              distillation or eval products. Image inputs over 8MB are dropped if storage is
              enabled.

          stream: If true, the model response data is streamed to the client as it is generated
              using Server-Sent Events.

          stream_options: Options for streaming responses. Only set when 'stream' is true (supports
              'include_usage' and 'include_obfuscation').

          system: System prompt/instructions. Anthropic: pass-through. Google: converted to
              systemInstruction. OpenAI: extracted from messages.

          temperature: What sampling temperature to use, between 0 and 2. Higher values like 0.8 make
              the output more random, while lower values like 0.2 make it more focused and
              deterministic. We generally recommend altering this or 'top_p' but not both.

          thinking: Extended thinking configuration (Anthropic only). Enables thinking blocks
              showing reasoning process. Requires min 1,024 token budget.

          tool_choice: Controls which (if any) tool is called by the model. 'none' stops tool calling,
              'auto' lets the model decide, and 'required' forces at least one tool
              invocation. Specific tool payloads force that tool.

          tool_config: Google tool configuration (function calling mode, etc.).

          tools: A list of tools the model may call. Supports OpenAI function tools and custom
              tools; use 'mcp_servers' for Dedalus-managed server-side tools.

          top_k: Top-k sampling. Anthropic: pass-through. Google: injected into
              generationConfig.topK.

          top_logprobs: An integer between 0 and 20 specifying how many of the most likely tokens to
              return at each position, with log probabilities. Requires 'logprobs' to be true.

          top_p: An alternative to sampling with temperature, called nucleus sampling, where the
              model considers the results of the tokens with top_p probability mass. So 0.1
              means only the tokens comprising the top 10% probability mass are considered. We
              generally recommend altering this or 'temperature' but not both.

          user: Stable identifier for your end-users. Helps OpenAI detect and prevent abuse and
              may boost cache hit rates. This field is being replaced by 'safety_identifier'
              and 'prompt_cache_key'.

          verbosity: Constrains the verbosity of the model's response. Lower values produce concise
              answers, higher values allow more detail.

          web_search_options: Configuration for OpenAI's web search tool. Learn more at
              https://platform.openai.com/docs/guides/tools-web-search?api-mode=chat.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds

          idempotency_key: Specify a custom idempotency key for this request
        """
        ...

    @overload
    def create(
        self,
        *,
        messages: Union[Iterable[Dict[str, object]], str],
        model: completion_create_params.Model,
        stream: Literal[True],
        agent_attributes: Optional[Dict[str, float]] | Omit = omit,
        audio: Optional[Dict[str, object]] | Omit = omit,
        disable_automatic_function_calling: Optional[bool] | Omit = omit,
        frequency_penalty: Optional[float] | Omit = omit,
        function_call: Union[str, Dict[str, object], None] | Omit = omit,
        functions: Optional[Iterable[Dict[str, object]]] | Omit = omit,
        generation_config: Optional[Dict[str, object]] | Omit = omit,
        guardrails: Optional[Iterable[Dict[str, object]]] | Omit = omit,
        handoff_config: Optional[Dict[str, object]] | Omit = omit,
        input: Union[Iterable[Dict[str, object]], str, None] | Omit = omit,
        instructions: Union[str, Iterable[Dict[str, object]], None] | Omit = omit,
        logit_bias: Optional[Dict[str, int]] | Omit = omit,
        logprobs: Optional[bool] | Omit = omit,
        max_completion_tokens: Optional[int] | Omit = omit,
        max_tokens: Optional[int] | Omit = omit,
        max_turns: Optional[int] | Omit = omit,
        mcp_servers: Optional[completion_create_params.MCPServers] | Omit = omit,
        metadata: Optional[Dict[str, str]] | Omit = omit,
        modalities: Optional[SequenceNotStr[str]] | Omit = omit,
        model_attributes: Optional[Dict[str, Dict[str, float]]] | Omit = omit,
        n: Optional[int] | Omit = omit,
        parallel_tool_calls: Optional[bool] | Omit = omit,
        prediction: Optional[Dict[str, object]] | Omit = omit,
        presence_penalty: Optional[float] | Omit = omit,
        prompt_cache_key: Optional[str] | Omit = omit,
        reasoning_effort: Optional[Literal["low", "medium", "high"]] | Omit = omit,
        response_format: Optional[Dict[str, object]] | Omit = omit,
        safety_identifier: Optional[str] | Omit = omit,
        safety_settings: Optional[Iterable[Dict[str, object]]] | Omit = omit,
        seed: Optional[int] | Omit = omit,
        service_tier: Optional[Literal["auto", "default"]] | Omit = omit,
        stop: Optional[SequenceNotStr[str]] | Omit = omit,
        store: Optional[bool] | Omit = omit,
        stream_options: Optional[Dict[str, object]] | Omit = omit,
        system: Union[str, Iterable[Dict[str, object]], None] | Omit = omit,
        temperature: Optional[float] | Omit = omit,
        thinking: Optional[completion_create_params.Thinking] | Omit = omit,
        tool_choice: Union[str, Dict[str, object], None] | Omit = omit,
        tool_config: Optional[Dict[str, object]] | Omit = omit,
        tools: Optional[Iterable[Dict[str, object]]] | Omit = omit,
        top_k: Optional[int] | Omit = omit,
        top_logprobs: Optional[int] | Omit = omit,
        top_p: Optional[float] | Omit = omit,
        user: Optional[str] | Omit = omit,
        verbosity: Optional[Literal["low", "medium", "high"]] | Omit = omit,
        web_search_options: Optional[Dict[str, object]] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
        idempotency_key: str | None = None,
    ) -> Stream[StreamChunk]:
        """
        Create a chat completion.

        This endpoint provides a vendor-agnostic chat completions API that works with
        thousands of LLMs. It supports MCP integration, multi-model routing with
        intelligent agentic handoffs, client-side and server-side tool execution, and
        streaming and non-streaming responses.

        Args: request: Chat completion request with messages, model, and configuration.
        http_request: FastAPI request object for accessing headers and state.
        background_tasks: FastAPI background tasks for async billing operations. user:
        Authenticated user with validated API key and sufficient balance.

        Returns: ChatCompletion: OpenAI-compatible completion response with usage data.

        Raises: HTTPException: - 401 if authentication fails or insufficient balance. -
        400 if request validation fails. - 500 if internal processing error occurs.

        Billing: - Token usage billed automatically based on model pricing - MCP tool
        calls billed separately using credits system - Streaming responses billed after
        completion via background task

        Example: Basic chat completion: ```python from dedalus_labs import Dedalus

            client = Dedalus(api_key="your-api-key")

            completion = client.chat.completions.create(
                model="openai/gpt-5",
                messages=[{"role": "user", "content": "Hello, how are you?"}],
            )

            print(completion.choices[0].message.content)
            ```

            With tools and MCP servers:
            ```python
            completion = client.chat.completions.create(
                model="openai/gpt-5",
                messages=[{"role": "user", "content": "Search for recent AI news"}],
                tools=[
                    {
                        "type": "function",
                        "function": {
                            "name": "search_web",
                            "description": "Search the web for information",
                        },
                    }
                ],
                mcp_servers=["dedalus-labs/brave-search"],
            )
            ```

            Multi-model routing:
            ```python
            completion = client.chat.completions.create(
                model=[
                    "openai/gpt-4o-mini",
                    "openai/gpt-5",
                    "anthropic/claude-sonnet-4-20250514",
                ],
                messages=[{"role": "user", "content": "Analyze this complex data"}],
                agent_attributes={"complexity": 0.8, "accuracy": 0.9},
            )
            ```

            Streaming response:
            ```python
            stream = client.chat.completions.create(
                model="openai/gpt-5",
                messages=[{"role": "user", "content": "Tell me a story"}],
                stream=True,
            )

            for chunk in stream:
                if chunk.choices[0].delta.content:
                    print(chunk.choices[0].delta.content, end="")
            ```

        Args:
          messages: Conversation history. Accepts either a list of message objects or a string,
              which is treated as a single user message.

          model: Model(s) to use for completion. Can be a single model ID, a DedalusModel object,
              or a list for multi-model routing. Single model: 'openai/gpt-4',
              'anthropic/claude-3-5-sonnet-20241022', 'openai/gpt-4o-mini', or a DedalusModel
              instance. Multi-model routing: ['openai/gpt-4o-mini', 'openai/gpt-4',
              'anthropic/claude-3-5-sonnet'] or list of DedalusModel objects - agent will
              choose optimal model based on task complexity.

          stream: If true, the model response data is streamed to the client as it is generated
              using Server-Sent Events.

          agent_attributes: Attributes for the agent itself, influencing behavior and model selection.
              Format: {'attribute': value}, where values are 0.0-1.0. Common attributes:
              'complexity', 'accuracy', 'efficiency', 'creativity', 'friendliness'. Higher
              values indicate stronger preference for that characteristic.

          audio: Parameters for audio output. Required when requesting audio responses (for
              example, modalities including 'audio').

          disable_automatic_function_calling: Google-only flag to disable the SDK's automatic function execution. When true,
              the model returns function calls for the client to execute manually.

          frequency_penalty: Number between -2.0 and 2.0. Positive values penalize new tokens based on their
              existing frequency in the text so far, decreasing the model's likelihood to
              repeat the same line verbatim.

          function_call: Deprecated in favor of 'tool_choice'. Controls which function is called by the
              model (none, auto, or specific name).

          functions: Deprecated in favor of 'tools'. Legacy list of function definitions the model
              may generate JSON inputs for.

          generation_config: Google generationConfig object. Merged with auto-generated config. Use for
              Google-specific params (candidateCount, responseMimeType, etc.).

          guardrails: Guardrails to apply to the agent for input/output validation and safety checks.
              Reserved for future use - guardrails configuration format not yet finalized.

          handoff_config: Configuration for multi-model handoffs and agent orchestration. Reserved for
              future use - handoff configuration format not yet finalized.

          input: Convenience alias for Responses-style `input`. Used when `messages` is omitted
              to provide the user prompt directly.

          instructions: Convenience alias for Responses-style `instructions`. Takes precedence over
              `system` and over system-role messages when provided.

          logit_bias: Modify the likelihood of specified tokens appearing in the completion. Accepts a
              JSON object mapping token IDs (as strings) to bias values from -100 to 100. The
              bias is added to the logits before sampling; values between -1 and 1 nudge
              selection probability, while values like -100 or 100 effectively ban or require
              a token.

          logprobs: Whether to return log probabilities of the output tokens. If true, returns the
              log probabilities for each token in the response content.

          max_completion_tokens: An upper bound for the number of tokens that can be generated for a completion,
              including visible output and reasoning tokens.

          max_tokens: The maximum number of tokens that can be generated in the chat completion. This
              value can be used to control costs for text generated via API. This value is now
              deprecated in favor of 'max_completion_tokens' and is not compatible with
              o-series models.

          max_turns: Maximum number of turns for agent execution before terminating (default: 10).
              Each turn represents one model inference cycle. Higher values allow more complex
              reasoning but increase cost and latency.

          mcp_servers: MCP (Model Context Protocol) server addresses to make available for server-side
              tool execution. Entries can be URLs (e.g., 'https://mcp.example.com'), slugs
              (e.g., 'dedalus-labs/brave-search'), or structured objects specifying
              slug/version/url. MCP tools are executed server-side and billed separately.

          metadata: Set of up to 16 key-value string pairs that can be attached to the request for
              structured metadata.

          modalities: Output types you would like the model to generate. Most models default to
              ['text']; some support ['text', 'audio'].

          model_attributes: Attributes for individual models used in routing decisions during multi-model
              execution. Format: {'model_name': {'attribute': value}}, where values are
              0.0-1.0. Common attributes: 'intelligence', 'speed', 'cost', 'creativity',
              'accuracy'. Used by agent to select optimal model based on task requirements.

          n: How many chat completion choices to generate for each input message. Keep 'n' as
              1 to minimize costs.

          parallel_tool_calls: Whether to enable parallel function calling during tool use.

          prediction: Configuration for predicted outputs. Improves response times when you already
              know large portions of the response content.

          presence_penalty: Number between -2.0 and 2.0. Positive values penalize new tokens based on
              whether they appear in the text so far, increasing the model's likelihood to
              talk about new topics.

          prompt_cache_key: Used by OpenAI to cache responses for similar requests and optimize cache hit
              rates. Replaces the legacy 'user' field for caching.

          reasoning_effort: Constrains effort on reasoning for supported reasoning models. Higher values use
              more compute, potentially improving reasoning quality at the cost of latency and
              tokens.

          response_format:
              An object specifying the format that the model must output. Use {'type':
              'json_schema', 'json_schema': {...}} for structured outputs or {'type':
              'json_object'} for the legacy JSON mode. Currently only OpenAI-prefixed models
              honour this field; Anthropic and Google requests will return an
              invalid_request_error if it is supplied.

          safety_identifier: Stable identifier used to help detect users who might violate OpenAI usage
              policies. Consider hashing end-user identifiers before sending.

          safety_settings: Google safety settings (harm categories and thresholds).

          seed: If specified, system will make a best effort to sample deterministically.
              Determinism is not guaranteed for the same seed across different models or API
              versions.

          service_tier: Specifies the processing tier used for the request. 'auto' uses project
              defaults, while 'default' forces standard pricing and performance.

          stop: Not supported with latest reasoning models 'o3' and 'o4-mini'.

                      Up to 4 sequences where the API will stop generating further tokens; the returned text will not contain the stop sequence.

          store: Whether to store the output of this chat completion request for OpenAI model
              distillation or eval products. Image inputs over 8MB are dropped if storage is
              enabled.

          stream_options: Options for streaming responses. Only set when 'stream' is true (supports
              'include_usage' and 'include_obfuscation').

          system: System prompt/instructions. Anthropic: pass-through. Google: converted to
              systemInstruction. OpenAI: extracted from messages.

          temperature: What sampling temperature to use, between 0 and 2. Higher values like 0.8 make
              the output more random, while lower values like 0.2 make it more focused and
              deterministic. We generally recommend altering this or 'top_p' but not both.

          thinking: Extended thinking configuration (Anthropic only). Enables thinking blocks
              showing reasoning process. Requires min 1,024 token budget.

          tool_choice: Controls which (if any) tool is called by the model. 'none' stops tool calling,
              'auto' lets the model decide, and 'required' forces at least one tool
              invocation. Specific tool payloads force that tool.

          tool_config: Google tool configuration (function calling mode, etc.).

          tools: A list of tools the model may call. Supports OpenAI function tools and custom
              tools; use 'mcp_servers' for Dedalus-managed server-side tools.

          top_k: Top-k sampling. Anthropic: pass-through. Google: injected into
              generationConfig.topK.

          top_logprobs: An integer between 0 and 20 specifying how many of the most likely tokens to
              return at each position, with log probabilities. Requires 'logprobs' to be true.

          top_p: An alternative to sampling with temperature, called nucleus sampling, where the
              model considers the results of the tokens with top_p probability mass. So 0.1
              means only the tokens comprising the top 10% probability mass are considered. We
              generally recommend altering this or 'temperature' but not both.

          user: Stable identifier for your end-users. Helps OpenAI detect and prevent abuse and
              may boost cache hit rates. This field is being replaced by 'safety_identifier'
              and 'prompt_cache_key'.

          verbosity: Constrains the verbosity of the model's response. Lower values produce concise
              answers, higher values allow more detail.

          web_search_options: Configuration for OpenAI's web search tool. Learn more at
              https://platform.openai.com/docs/guides/tools-web-search?api-mode=chat.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds

          idempotency_key: Specify a custom idempotency key for this request
        """
        ...

    @overload
    def create(
        self,
        *,
        messages: Union[Iterable[Dict[str, object]], str],
        model: completion_create_params.Model,
        stream: bool,
        agent_attributes: Optional[Dict[str, float]] | Omit = omit,
        audio: Optional[Dict[str, object]] | Omit = omit,
        disable_automatic_function_calling: Optional[bool] | Omit = omit,
        frequency_penalty: Optional[float] | Omit = omit,
        function_call: Union[str, Dict[str, object], None] | Omit = omit,
        functions: Optional[Iterable[Dict[str, object]]] | Omit = omit,
        generation_config: Optional[Dict[str, object]] | Omit = omit,
        guardrails: Optional[Iterable[Dict[str, object]]] | Omit = omit,
        handoff_config: Optional[Dict[str, object]] | Omit = omit,
        input: Union[Iterable[Dict[str, object]], str, None] | Omit = omit,
        instructions: Union[str, Iterable[Dict[str, object]], None] | Omit = omit,
        logit_bias: Optional[Dict[str, int]] | Omit = omit,
        logprobs: Optional[bool] | Omit = omit,
        max_completion_tokens: Optional[int] | Omit = omit,
        max_tokens: Optional[int] | Omit = omit,
        max_turns: Optional[int] | Omit = omit,
        mcp_servers: Optional[completion_create_params.MCPServers] | Omit = omit,
        metadata: Optional[Dict[str, str]] | Omit = omit,
        modalities: Optional[SequenceNotStr[str]] | Omit = omit,
        model_attributes: Optional[Dict[str, Dict[str, float]]] | Omit = omit,
        n: Optional[int] | Omit = omit,
        parallel_tool_calls: Optional[bool] | Omit = omit,
        prediction: Optional[Dict[str, object]] | Omit = omit,
        presence_penalty: Optional[float] | Omit = omit,
        prompt_cache_key: Optional[str] | Omit = omit,
        reasoning_effort: Optional[Literal["low", "medium", "high"]] | Omit = omit,
        response_format: Optional[Dict[str, object]] | Omit = omit,
        safety_identifier: Optional[str] | Omit = omit,
        safety_settings: Optional[Iterable[Dict[str, object]]] | Omit = omit,
        seed: Optional[int] | Omit = omit,
        service_tier: Optional[Literal["auto", "default"]] | Omit = omit,
        stop: Optional[SequenceNotStr[str]] | Omit = omit,
        store: Optional[bool] | Omit = omit,
        stream_options: Optional[Dict[str, object]] | Omit = omit,
        system: Union[str, Iterable[Dict[str, object]], None] | Omit = omit,
        temperature: Optional[float] | Omit = omit,
        thinking: Optional[completion_create_params.Thinking] | Omit = omit,
        tool_choice: Union[str, Dict[str, object], None] | Omit = omit,
        tool_config: Optional[Dict[str, object]] | Omit = omit,
        tools: Optional[Iterable[Dict[str, object]]] | Omit = omit,
        top_k: Optional[int] | Omit = omit,
        top_logprobs: Optional[int] | Omit = omit,
        top_p: Optional[float] | Omit = omit,
        user: Optional[str] | Omit = omit,
        verbosity: Optional[Literal["low", "medium", "high"]] | Omit = omit,
        web_search_options: Optional[Dict[str, object]] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
        idempotency_key: str | None = None,
    ) -> StreamChunk | Stream[StreamChunk]:
        """
        Create a chat completion.

        This endpoint provides a vendor-agnostic chat completions API that works with
        thousands of LLMs. It supports MCP integration, multi-model routing with
        intelligent agentic handoffs, client-side and server-side tool execution, and
        streaming and non-streaming responses.

        Args: request: Chat completion request with messages, model, and configuration.
        http_request: FastAPI request object for accessing headers and state.
        background_tasks: FastAPI background tasks for async billing operations. user:
        Authenticated user with validated API key and sufficient balance.

        Returns: ChatCompletion: OpenAI-compatible completion response with usage data.

        Raises: HTTPException: - 401 if authentication fails or insufficient balance. -
        400 if request validation fails. - 500 if internal processing error occurs.

        Billing: - Token usage billed automatically based on model pricing - MCP tool
        calls billed separately using credits system - Streaming responses billed after
        completion via background task

        Example: Basic chat completion: ```python from dedalus_labs import Dedalus

            client = Dedalus(api_key="your-api-key")

            completion = client.chat.completions.create(
                model="openai/gpt-5",
                messages=[{"role": "user", "content": "Hello, how are you?"}],
            )

            print(completion.choices[0].message.content)
            ```

            With tools and MCP servers:
            ```python
            completion = client.chat.completions.create(
                model="openai/gpt-5",
                messages=[{"role": "user", "content": "Search for recent AI news"}],
                tools=[
                    {
                        "type": "function",
                        "function": {
                            "name": "search_web",
                            "description": "Search the web for information",
                        },
                    }
                ],
                mcp_servers=["dedalus-labs/brave-search"],
            )
            ```

            Multi-model routing:
            ```python
            completion = client.chat.completions.create(
                model=[
                    "openai/gpt-4o-mini",
                    "openai/gpt-5",
                    "anthropic/claude-sonnet-4-20250514",
                ],
                messages=[{"role": "user", "content": "Analyze this complex data"}],
                agent_attributes={"complexity": 0.8, "accuracy": 0.9},
            )
            ```

            Streaming response:
            ```python
            stream = client.chat.completions.create(
                model="openai/gpt-5",
                messages=[{"role": "user", "content": "Tell me a story"}],
                stream=True,
            )

            for chunk in stream:
                if chunk.choices[0].delta.content:
                    print(chunk.choices[0].delta.content, end="")
            ```

        Args:
          messages: Conversation history. Accepts either a list of message objects or a string,
              which is treated as a single user message.

          model: Model(s) to use for completion. Can be a single model ID, a DedalusModel object,
              or a list for multi-model routing. Single model: 'openai/gpt-4',
              'anthropic/claude-3-5-sonnet-20241022', 'openai/gpt-4o-mini', or a DedalusModel
              instance. Multi-model routing: ['openai/gpt-4o-mini', 'openai/gpt-4',
              'anthropic/claude-3-5-sonnet'] or list of DedalusModel objects - agent will
              choose optimal model based on task complexity.

          stream: If true, the model response data is streamed to the client as it is generated
              using Server-Sent Events.

          agent_attributes: Attributes for the agent itself, influencing behavior and model selection.
              Format: {'attribute': value}, where values are 0.0-1.0. Common attributes:
              'complexity', 'accuracy', 'efficiency', 'creativity', 'friendliness'. Higher
              values indicate stronger preference for that characteristic.

          audio: Parameters for audio output. Required when requesting audio responses (for
              example, modalities including 'audio').

          disable_automatic_function_calling: Google-only flag to disable the SDK's automatic function execution. When true,
              the model returns function calls for the client to execute manually.

          frequency_penalty: Number between -2.0 and 2.0. Positive values penalize new tokens based on their
              existing frequency in the text so far, decreasing the model's likelihood to
              repeat the same line verbatim.

          function_call: Deprecated in favor of 'tool_choice'. Controls which function is called by the
              model (none, auto, or specific name).

          functions: Deprecated in favor of 'tools'. Legacy list of function definitions the model
              may generate JSON inputs for.

          generation_config: Google generationConfig object. Merged with auto-generated config. Use for
              Google-specific params (candidateCount, responseMimeType, etc.).

          guardrails: Guardrails to apply to the agent for input/output validation and safety checks.
              Reserved for future use - guardrails configuration format not yet finalized.

          handoff_config: Configuration for multi-model handoffs and agent orchestration. Reserved for
              future use - handoff configuration format not yet finalized.

          input: Convenience alias for Responses-style `input`. Used when `messages` is omitted
              to provide the user prompt directly.

          instructions: Convenience alias for Responses-style `instructions`. Takes precedence over
              `system` and over system-role messages when provided.

          logit_bias: Modify the likelihood of specified tokens appearing in the completion. Accepts a
              JSON object mapping token IDs (as strings) to bias values from -100 to 100. The
              bias is added to the logits before sampling; values between -1 and 1 nudge
              selection probability, while values like -100 or 100 effectively ban or require
              a token.

          logprobs: Whether to return log probabilities of the output tokens. If true, returns the
              log probabilities for each token in the response content.

          max_completion_tokens: An upper bound for the number of tokens that can be generated for a completion,
              including visible output and reasoning tokens.

          max_tokens: The maximum number of tokens that can be generated in the chat completion. This
              value can be used to control costs for text generated via API. This value is now
              deprecated in favor of 'max_completion_tokens' and is not compatible with
              o-series models.

          max_turns: Maximum number of turns for agent execution before terminating (default: 10).
              Each turn represents one model inference cycle. Higher values allow more complex
              reasoning but increase cost and latency.

          mcp_servers: MCP (Model Context Protocol) server addresses to make available for server-side
              tool execution. Entries can be URLs (e.g., 'https://mcp.example.com'), slugs
              (e.g., 'dedalus-labs/brave-search'), or structured objects specifying
              slug/version/url. MCP tools are executed server-side and billed separately.

          metadata: Set of up to 16 key-value string pairs that can be attached to the request for
              structured metadata.

          modalities: Output types you would like the model to generate. Most models default to
              ['text']; some support ['text', 'audio'].

          model_attributes: Attributes for individual models used in routing decisions during multi-model
              execution. Format: {'model_name': {'attribute': value}}, where values are
              0.0-1.0. Common attributes: 'intelligence', 'speed', 'cost', 'creativity',
              'accuracy'. Used by agent to select optimal model based on task requirements.

          n: How many chat completion choices to generate for each input message. Keep 'n' as
              1 to minimize costs.

          parallel_tool_calls: Whether to enable parallel function calling during tool use.

          prediction: Configuration for predicted outputs. Improves response times when you already
              know large portions of the response content.

          presence_penalty: Number between -2.0 and 2.0. Positive values penalize new tokens based on
              whether they appear in the text so far, increasing the model's likelihood to
              talk about new topics.

          prompt_cache_key: Used by OpenAI to cache responses for similar requests and optimize cache hit
              rates. Replaces the legacy 'user' field for caching.

          reasoning_effort: Constrains effort on reasoning for supported reasoning models. Higher values use
              more compute, potentially improving reasoning quality at the cost of latency and
              tokens.

          response_format:
              An object specifying the format that the model must output. Use {'type':
              'json_schema', 'json_schema': {...}} for structured outputs or {'type':
              'json_object'} for the legacy JSON mode. Currently only OpenAI-prefixed models
              honour this field; Anthropic and Google requests will return an
              invalid_request_error if it is supplied.

          safety_identifier: Stable identifier used to help detect users who might violate OpenAI usage
              policies. Consider hashing end-user identifiers before sending.

          safety_settings: Google safety settings (harm categories and thresholds).

          seed: If specified, system will make a best effort to sample deterministically.
              Determinism is not guaranteed for the same seed across different models or API
              versions.

          service_tier: Specifies the processing tier used for the request. 'auto' uses project
              defaults, while 'default' forces standard pricing and performance.

          stop: Not supported with latest reasoning models 'o3' and 'o4-mini'.

                      Up to 4 sequences where the API will stop generating further tokens; the returned text will not contain the stop sequence.

          store: Whether to store the output of this chat completion request for OpenAI model
              distillation or eval products. Image inputs over 8MB are dropped if storage is
              enabled.

          stream_options: Options for streaming responses. Only set when 'stream' is true (supports
              'include_usage' and 'include_obfuscation').

          system: System prompt/instructions. Anthropic: pass-through. Google: converted to
              systemInstruction. OpenAI: extracted from messages.

          temperature: What sampling temperature to use, between 0 and 2. Higher values like 0.8 make
              the output more random, while lower values like 0.2 make it more focused and
              deterministic. We generally recommend altering this or 'top_p' but not both.

          thinking: Extended thinking configuration (Anthropic only). Enables thinking blocks
              showing reasoning process. Requires min 1,024 token budget.

          tool_choice: Controls which (if any) tool is called by the model. 'none' stops tool calling,
              'auto' lets the model decide, and 'required' forces at least one tool
              invocation. Specific tool payloads force that tool.

          tool_config: Google tool configuration (function calling mode, etc.).

          tools: A list of tools the model may call. Supports OpenAI function tools and custom
              tools; use 'mcp_servers' for Dedalus-managed server-side tools.

          top_k: Top-k sampling. Anthropic: pass-through. Google: injected into
              generationConfig.topK.

          top_logprobs: An integer between 0 and 20 specifying how many of the most likely tokens to
              return at each position, with log probabilities. Requires 'logprobs' to be true.

          top_p: An alternative to sampling with temperature, called nucleus sampling, where the
              model considers the results of the tokens with top_p probability mass. So 0.1
              means only the tokens comprising the top 10% probability mass are considered. We
              generally recommend altering this or 'temperature' but not both.

          user: Stable identifier for your end-users. Helps OpenAI detect and prevent abuse and
              may boost cache hit rates. This field is being replaced by 'safety_identifier'
              and 'prompt_cache_key'.

          verbosity: Constrains the verbosity of the model's response. Lower values produce concise
              answers, higher values allow more detail.

          web_search_options: Configuration for OpenAI's web search tool. Learn more at
              https://platform.openai.com/docs/guides/tools-web-search?api-mode=chat.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds

          idempotency_key: Specify a custom idempotency key for this request
        """
        ...

    @required_args(["messages", "model"], ["messages", "model", "stream"])
    def create(
        self,
        *,
        messages: Union[Iterable[Dict[str, object]], str],
        model: completion_create_params.Model,
        agent_attributes: Optional[Dict[str, float]] | Omit = omit,
        audio: Optional[Dict[str, object]] | Omit = omit,
        disable_automatic_function_calling: Optional[bool] | Omit = omit,
        frequency_penalty: Optional[float] | Omit = omit,
        function_call: Union[str, Dict[str, object], None] | Omit = omit,
        functions: Optional[Iterable[Dict[str, object]]] | Omit = omit,
        generation_config: Optional[Dict[str, object]] | Omit = omit,
        guardrails: Optional[Iterable[Dict[str, object]]] | Omit = omit,
        handoff_config: Optional[Dict[str, object]] | Omit = omit,
        input: Union[Iterable[Dict[str, object]], str, None] | Omit = omit,
        instructions: Union[str, Iterable[Dict[str, object]], None] | Omit = omit,
        logit_bias: Optional[Dict[str, int]] | Omit = omit,
        logprobs: Optional[bool] | Omit = omit,
        max_completion_tokens: Optional[int] | Omit = omit,
        max_tokens: Optional[int] | Omit = omit,
        max_turns: Optional[int] | Omit = omit,
        mcp_servers: Optional[completion_create_params.MCPServers] | Omit = omit,
        metadata: Optional[Dict[str, str]] | Omit = omit,
        modalities: Optional[SequenceNotStr[str]] | Omit = omit,
        model_attributes: Optional[Dict[str, Dict[str, float]]] | Omit = omit,
        n: Optional[int] | Omit = omit,
        parallel_tool_calls: Optional[bool] | Omit = omit,
        prediction: Optional[Dict[str, object]] | Omit = omit,
        presence_penalty: Optional[float] | Omit = omit,
        prompt_cache_key: Optional[str] | Omit = omit,
        reasoning_effort: Optional[Literal["low", "medium", "high"]] | Omit = omit,
        response_format: Optional[Dict[str, object]] | Omit = omit,
        safety_identifier: Optional[str] | Omit = omit,
        safety_settings: Optional[Iterable[Dict[str, object]]] | Omit = omit,
        seed: Optional[int] | Omit = omit,
        service_tier: Optional[Literal["auto", "default"]] | Omit = omit,
        stop: Optional[SequenceNotStr[str]] | Omit = omit,
        store: Optional[bool] | Omit = omit,
        stream: Literal[False] | Literal[True] | Omit = omit,
        stream_options: Optional[Dict[str, object]] | Omit = omit,
        system: Union[str, Iterable[Dict[str, object]], None] | Omit = omit,
        temperature: Optional[float] | Omit = omit,
        thinking: Optional[completion_create_params.Thinking] | Omit = omit,
        tool_choice: Union[str, Dict[str, object], None] | Omit = omit,
        tool_config: Optional[Dict[str, object]] | Omit = omit,
        tools: Optional[Iterable[Dict[str, object]]] | Omit = omit,
        top_k: Optional[int] | Omit = omit,
        top_logprobs: Optional[int] | Omit = omit,
        top_p: Optional[float] | Omit = omit,
        user: Optional[str] | Omit = omit,
        verbosity: Optional[Literal["low", "medium", "high"]] | Omit = omit,
        web_search_options: Optional[Dict[str, object]] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
        idempotency_key: str | None = None,
    ) -> StreamChunk | Stream[StreamChunk]:
        return self._post(
            "/v1/chat/completions",
            body=maybe_transform(
                {
                    "messages": messages,
                    "model": model,
                    "agent_attributes": agent_attributes,
                    "audio": audio,
                    "disable_automatic_function_calling": disable_automatic_function_calling,
                    "frequency_penalty": frequency_penalty,
                    "function_call": function_call,
                    "functions": functions,
                    "generation_config": generation_config,
                    "guardrails": guardrails,
                    "handoff_config": handoff_config,
                    "input": input,
                    "instructions": instructions,
                    "logit_bias": logit_bias,
                    "logprobs": logprobs,
                    "max_completion_tokens": max_completion_tokens,
                    "max_tokens": max_tokens,
                    "max_turns": max_turns,
                    "mcp_servers": mcp_servers,
                    "metadata": metadata,
                    "modalities": modalities,
                    "model_attributes": model_attributes,
                    "n": n,
                    "parallel_tool_calls": parallel_tool_calls,
                    "prediction": prediction,
                    "presence_penalty": presence_penalty,
                    "prompt_cache_key": prompt_cache_key,
                    "reasoning_effort": reasoning_effort,
                    "response_format": response_format,
                    "safety_identifier": safety_identifier,
                    "safety_settings": safety_settings,
                    "seed": seed,
                    "service_tier": service_tier,
                    "stop": stop,
                    "store": store,
                    "stream": stream,
                    "stream_options": stream_options,
                    "system": system,
                    "temperature": temperature,
                    "thinking": thinking,
                    "tool_choice": tool_choice,
                    "tool_config": tool_config,
                    "tools": tools,
                    "top_k": top_k,
                    "top_logprobs": top_logprobs,
                    "top_p": top_p,
                    "user": user,
                    "verbosity": verbosity,
                    "web_search_options": web_search_options,
                },
                completion_create_params.CompletionCreateParamsStreaming
                if stream
                else completion_create_params.CompletionCreateParamsNonStreaming,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
            ),
            cast_to=StreamChunk,
            stream=stream or False,
            stream_cls=Stream[StreamChunk],
        )


class AsyncCompletionsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncCompletionsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/dedalus-labs/dedalus-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncCompletionsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncCompletionsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/dedalus-labs/dedalus-sdk-python#with_streaming_response
        """
        return AsyncCompletionsResourceWithStreamingResponse(self)

    @overload
    async def create(
        self,
        *,
        messages: Union[Iterable[Dict[str, object]], str],
        model: completion_create_params.Model,
        agent_attributes: Optional[Dict[str, float]] | Omit = omit,
        audio: Optional[Dict[str, object]] | Omit = omit,
        disable_automatic_function_calling: Optional[bool] | Omit = omit,
        frequency_penalty: Optional[float] | Omit = omit,
        function_call: Union[str, Dict[str, object], None] | Omit = omit,
        functions: Optional[Iterable[Dict[str, object]]] | Omit = omit,
        generation_config: Optional[Dict[str, object]] | Omit = omit,
        guardrails: Optional[Iterable[Dict[str, object]]] | Omit = omit,
        handoff_config: Optional[Dict[str, object]] | Omit = omit,
        input: Union[Iterable[Dict[str, object]], str, None] | Omit = omit,
        instructions: Union[str, Iterable[Dict[str, object]], None] | Omit = omit,
        logit_bias: Optional[Dict[str, int]] | Omit = omit,
        logprobs: Optional[bool] | Omit = omit,
        max_completion_tokens: Optional[int] | Omit = omit,
        max_tokens: Optional[int] | Omit = omit,
        max_turns: Optional[int] | Omit = omit,
        mcp_servers: Optional[completion_create_params.MCPServers] | Omit = omit,
        metadata: Optional[Dict[str, str]] | Omit = omit,
        modalities: Optional[SequenceNotStr[str]] | Omit = omit,
        model_attributes: Optional[Dict[str, Dict[str, float]]] | Omit = omit,
        n: Optional[int] | Omit = omit,
        parallel_tool_calls: Optional[bool] | Omit = omit,
        prediction: Optional[Dict[str, object]] | Omit = omit,
        presence_penalty: Optional[float] | Omit = omit,
        prompt_cache_key: Optional[str] | Omit = omit,
        reasoning_effort: Optional[Literal["low", "medium", "high"]] | Omit = omit,
        response_format: Optional[Dict[str, object]] | Omit = omit,
        safety_identifier: Optional[str] | Omit = omit,
        safety_settings: Optional[Iterable[Dict[str, object]]] | Omit = omit,
        seed: Optional[int] | Omit = omit,
        service_tier: Optional[Literal["auto", "default"]] | Omit = omit,
        stop: Optional[SequenceNotStr[str]] | Omit = omit,
        store: Optional[bool] | Omit = omit,
        stream: Literal[False] | Omit = omit,
        stream_options: Optional[Dict[str, object]] | Omit = omit,
        system: Union[str, Iterable[Dict[str, object]], None] | Omit = omit,
        temperature: Optional[float] | Omit = omit,
        thinking: Optional[completion_create_params.Thinking] | Omit = omit,
        tool_choice: Union[str, Dict[str, object], None] | Omit = omit,
        tool_config: Optional[Dict[str, object]] | Omit = omit,
        tools: Optional[Iterable[Dict[str, object]]] | Omit = omit,
        top_k: Optional[int] | Omit = omit,
        top_logprobs: Optional[int] | Omit = omit,
        top_p: Optional[float] | Omit = omit,
        user: Optional[str] | Omit = omit,
        verbosity: Optional[Literal["low", "medium", "high"]] | Omit = omit,
        web_search_options: Optional[Dict[str, object]] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
        idempotency_key: str | None = None,
    ) -> StreamChunk:
        """
        Create a chat completion.

        This endpoint provides a vendor-agnostic chat completions API that works with
        thousands of LLMs. It supports MCP integration, multi-model routing with
        intelligent agentic handoffs, client-side and server-side tool execution, and
        streaming and non-streaming responses.

        Args: request: Chat completion request with messages, model, and configuration.
        http_request: FastAPI request object for accessing headers and state.
        background_tasks: FastAPI background tasks for async billing operations. user:
        Authenticated user with validated API key and sufficient balance.

        Returns: ChatCompletion: OpenAI-compatible completion response with usage data.

        Raises: HTTPException: - 401 if authentication fails or insufficient balance. -
        400 if request validation fails. - 500 if internal processing error occurs.

        Billing: - Token usage billed automatically based on model pricing - MCP tool
        calls billed separately using credits system - Streaming responses billed after
        completion via background task

        Example: Basic chat completion: ```python from dedalus_labs import Dedalus

            client = Dedalus(api_key="your-api-key")

            completion = client.chat.completions.create(
                model="openai/gpt-5",
                messages=[{"role": "user", "content": "Hello, how are you?"}],
            )

            print(completion.choices[0].message.content)
            ```

            With tools and MCP servers:
            ```python
            completion = client.chat.completions.create(
                model="openai/gpt-5",
                messages=[{"role": "user", "content": "Search for recent AI news"}],
                tools=[
                    {
                        "type": "function",
                        "function": {
                            "name": "search_web",
                            "description": "Search the web for information",
                        },
                    }
                ],
                mcp_servers=["dedalus-labs/brave-search"],
            )
            ```

            Multi-model routing:
            ```python
            completion = client.chat.completions.create(
                model=[
                    "openai/gpt-4o-mini",
                    "openai/gpt-5",
                    "anthropic/claude-sonnet-4-20250514",
                ],
                messages=[{"role": "user", "content": "Analyze this complex data"}],
                agent_attributes={"complexity": 0.8, "accuracy": 0.9},
            )
            ```

            Streaming response:
            ```python
            stream = client.chat.completions.create(
                model="openai/gpt-5",
                messages=[{"role": "user", "content": "Tell me a story"}],
                stream=True,
            )

            for chunk in stream:
                if chunk.choices[0].delta.content:
                    print(chunk.choices[0].delta.content, end="")
            ```

        Args:
          messages: Conversation history. Accepts either a list of message objects or a string,
              which is treated as a single user message.

          model: Model(s) to use for completion. Can be a single model ID, a DedalusModel object,
              or a list for multi-model routing. Single model: 'openai/gpt-4',
              'anthropic/claude-3-5-sonnet-20241022', 'openai/gpt-4o-mini', or a DedalusModel
              instance. Multi-model routing: ['openai/gpt-4o-mini', 'openai/gpt-4',
              'anthropic/claude-3-5-sonnet'] or list of DedalusModel objects - agent will
              choose optimal model based on task complexity.

          agent_attributes: Attributes for the agent itself, influencing behavior and model selection.
              Format: {'attribute': value}, where values are 0.0-1.0. Common attributes:
              'complexity', 'accuracy', 'efficiency', 'creativity', 'friendliness'. Higher
              values indicate stronger preference for that characteristic.

          audio: Parameters for audio output. Required when requesting audio responses (for
              example, modalities including 'audio').

          disable_automatic_function_calling: Google-only flag to disable the SDK's automatic function execution. When true,
              the model returns function calls for the client to execute manually.

          frequency_penalty: Number between -2.0 and 2.0. Positive values penalize new tokens based on their
              existing frequency in the text so far, decreasing the model's likelihood to
              repeat the same line verbatim.

          function_call: Deprecated in favor of 'tool_choice'. Controls which function is called by the
              model (none, auto, or specific name).

          functions: Deprecated in favor of 'tools'. Legacy list of function definitions the model
              may generate JSON inputs for.

          generation_config: Google generationConfig object. Merged with auto-generated config. Use for
              Google-specific params (candidateCount, responseMimeType, etc.).

          guardrails: Guardrails to apply to the agent for input/output validation and safety checks.
              Reserved for future use - guardrails configuration format not yet finalized.

          handoff_config: Configuration for multi-model handoffs and agent orchestration. Reserved for
              future use - handoff configuration format not yet finalized.

          input: Convenience alias for Responses-style `input`. Used when `messages` is omitted
              to provide the user prompt directly.

          instructions: Convenience alias for Responses-style `instructions`. Takes precedence over
              `system` and over system-role messages when provided.

          logit_bias: Modify the likelihood of specified tokens appearing in the completion. Accepts a
              JSON object mapping token IDs (as strings) to bias values from -100 to 100. The
              bias is added to the logits before sampling; values between -1 and 1 nudge
              selection probability, while values like -100 or 100 effectively ban or require
              a token.

          logprobs: Whether to return log probabilities of the output tokens. If true, returns the
              log probabilities for each token in the response content.

          max_completion_tokens: An upper bound for the number of tokens that can be generated for a completion,
              including visible output and reasoning tokens.

          max_tokens: The maximum number of tokens that can be generated in the chat completion. This
              value can be used to control costs for text generated via API. This value is now
              deprecated in favor of 'max_completion_tokens' and is not compatible with
              o-series models.

          max_turns: Maximum number of turns for agent execution before terminating (default: 10).
              Each turn represents one model inference cycle. Higher values allow more complex
              reasoning but increase cost and latency.

          mcp_servers: MCP (Model Context Protocol) server addresses to make available for server-side
              tool execution. Entries can be URLs (e.g., 'https://mcp.example.com'), slugs
              (e.g., 'dedalus-labs/brave-search'), or structured objects specifying
              slug/version/url. MCP tools are executed server-side and billed separately.

          metadata: Set of up to 16 key-value string pairs that can be attached to the request for
              structured metadata.

          modalities: Output types you would like the model to generate. Most models default to
              ['text']; some support ['text', 'audio'].

          model_attributes: Attributes for individual models used in routing decisions during multi-model
              execution. Format: {'model_name': {'attribute': value}}, where values are
              0.0-1.0. Common attributes: 'intelligence', 'speed', 'cost', 'creativity',
              'accuracy'. Used by agent to select optimal model based on task requirements.

          n: How many chat completion choices to generate for each input message. Keep 'n' as
              1 to minimize costs.

          parallel_tool_calls: Whether to enable parallel function calling during tool use.

          prediction: Configuration for predicted outputs. Improves response times when you already
              know large portions of the response content.

          presence_penalty: Number between -2.0 and 2.0. Positive values penalize new tokens based on
              whether they appear in the text so far, increasing the model's likelihood to
              talk about new topics.

          prompt_cache_key: Used by OpenAI to cache responses for similar requests and optimize cache hit
              rates. Replaces the legacy 'user' field for caching.

          reasoning_effort: Constrains effort on reasoning for supported reasoning models. Higher values use
              more compute, potentially improving reasoning quality at the cost of latency and
              tokens.

          response_format:
              An object specifying the format that the model must output. Use {'type':
              'json_schema', 'json_schema': {...}} for structured outputs or {'type':
              'json_object'} for the legacy JSON mode. Currently only OpenAI-prefixed models
              honour this field; Anthropic and Google requests will return an
              invalid_request_error if it is supplied.

          safety_identifier: Stable identifier used to help detect users who might violate OpenAI usage
              policies. Consider hashing end-user identifiers before sending.

          safety_settings: Google safety settings (harm categories and thresholds).

          seed: If specified, system will make a best effort to sample deterministically.
              Determinism is not guaranteed for the same seed across different models or API
              versions.

          service_tier: Specifies the processing tier used for the request. 'auto' uses project
              defaults, while 'default' forces standard pricing and performance.

          stop: Not supported with latest reasoning models 'o3' and 'o4-mini'.

                      Up to 4 sequences where the API will stop generating further tokens; the returned text will not contain the stop sequence.

          store: Whether to store the output of this chat completion request for OpenAI model
              distillation or eval products. Image inputs over 8MB are dropped if storage is
              enabled.

          stream: If true, the model response data is streamed to the client as it is generated
              using Server-Sent Events.

          stream_options: Options for streaming responses. Only set when 'stream' is true (supports
              'include_usage' and 'include_obfuscation').

          system: System prompt/instructions. Anthropic: pass-through. Google: converted to
              systemInstruction. OpenAI: extracted from messages.

          temperature: What sampling temperature to use, between 0 and 2. Higher values like 0.8 make
              the output more random, while lower values like 0.2 make it more focused and
              deterministic. We generally recommend altering this or 'top_p' but not both.

          thinking: Extended thinking configuration (Anthropic only). Enables thinking blocks
              showing reasoning process. Requires min 1,024 token budget.

          tool_choice: Controls which (if any) tool is called by the model. 'none' stops tool calling,
              'auto' lets the model decide, and 'required' forces at least one tool
              invocation. Specific tool payloads force that tool.

          tool_config: Google tool configuration (function calling mode, etc.).

          tools: A list of tools the model may call. Supports OpenAI function tools and custom
              tools; use 'mcp_servers' for Dedalus-managed server-side tools.

          top_k: Top-k sampling. Anthropic: pass-through. Google: injected into
              generationConfig.topK.

          top_logprobs: An integer between 0 and 20 specifying how many of the most likely tokens to
              return at each position, with log probabilities. Requires 'logprobs' to be true.

          top_p: An alternative to sampling with temperature, called nucleus sampling, where the
              model considers the results of the tokens with top_p probability mass. So 0.1
              means only the tokens comprising the top 10% probability mass are considered. We
              generally recommend altering this or 'temperature' but not both.

          user: Stable identifier for your end-users. Helps OpenAI detect and prevent abuse and
              may boost cache hit rates. This field is being replaced by 'safety_identifier'
              and 'prompt_cache_key'.

          verbosity: Constrains the verbosity of the model's response. Lower values produce concise
              answers, higher values allow more detail.

          web_search_options: Configuration for OpenAI's web search tool. Learn more at
              https://platform.openai.com/docs/guides/tools-web-search?api-mode=chat.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds

          idempotency_key: Specify a custom idempotency key for this request
        """
        ...

    @overload
    async def create(
        self,
        *,
        messages: Union[Iterable[Dict[str, object]], str],
        model: completion_create_params.Model,
        stream: Literal[True],
        agent_attributes: Optional[Dict[str, float]] | Omit = omit,
        audio: Optional[Dict[str, object]] | Omit = omit,
        disable_automatic_function_calling: Optional[bool] | Omit = omit,
        frequency_penalty: Optional[float] | Omit = omit,
        function_call: Union[str, Dict[str, object], None] | Omit = omit,
        functions: Optional[Iterable[Dict[str, object]]] | Omit = omit,
        generation_config: Optional[Dict[str, object]] | Omit = omit,
        guardrails: Optional[Iterable[Dict[str, object]]] | Omit = omit,
        handoff_config: Optional[Dict[str, object]] | Omit = omit,
        input: Union[Iterable[Dict[str, object]], str, None] | Omit = omit,
        instructions: Union[str, Iterable[Dict[str, object]], None] | Omit = omit,
        logit_bias: Optional[Dict[str, int]] | Omit = omit,
        logprobs: Optional[bool] | Omit = omit,
        max_completion_tokens: Optional[int] | Omit = omit,
        max_tokens: Optional[int] | Omit = omit,
        max_turns: Optional[int] | Omit = omit,
        mcp_servers: Optional[completion_create_params.MCPServers] | Omit = omit,
        metadata: Optional[Dict[str, str]] | Omit = omit,
        modalities: Optional[SequenceNotStr[str]] | Omit = omit,
        model_attributes: Optional[Dict[str, Dict[str, float]]] | Omit = omit,
        n: Optional[int] | Omit = omit,
        parallel_tool_calls: Optional[bool] | Omit = omit,
        prediction: Optional[Dict[str, object]] | Omit = omit,
        presence_penalty: Optional[float] | Omit = omit,
        prompt_cache_key: Optional[str] | Omit = omit,
        reasoning_effort: Optional[Literal["low", "medium", "high"]] | Omit = omit,
        response_format: Optional[Dict[str, object]] | Omit = omit,
        safety_identifier: Optional[str] | Omit = omit,
        safety_settings: Optional[Iterable[Dict[str, object]]] | Omit = omit,
        seed: Optional[int] | Omit = omit,
        service_tier: Optional[Literal["auto", "default"]] | Omit = omit,
        stop: Optional[SequenceNotStr[str]] | Omit = omit,
        store: Optional[bool] | Omit = omit,
        stream_options: Optional[Dict[str, object]] | Omit = omit,
        system: Union[str, Iterable[Dict[str, object]], None] | Omit = omit,
        temperature: Optional[float] | Omit = omit,
        thinking: Optional[completion_create_params.Thinking] | Omit = omit,
        tool_choice: Union[str, Dict[str, object], None] | Omit = omit,
        tool_config: Optional[Dict[str, object]] | Omit = omit,
        tools: Optional[Iterable[Dict[str, object]]] | Omit = omit,
        top_k: Optional[int] | Omit = omit,
        top_logprobs: Optional[int] | Omit = omit,
        top_p: Optional[float] | Omit = omit,
        user: Optional[str] | Omit = omit,
        verbosity: Optional[Literal["low", "medium", "high"]] | Omit = omit,
        web_search_options: Optional[Dict[str, object]] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
        idempotency_key: str | None = None,
    ) -> AsyncStream[StreamChunk]:
        """
        Create a chat completion.

        This endpoint provides a vendor-agnostic chat completions API that works with
        thousands of LLMs. It supports MCP integration, multi-model routing with
        intelligent agentic handoffs, client-side and server-side tool execution, and
        streaming and non-streaming responses.

        Args: request: Chat completion request with messages, model, and configuration.
        http_request: FastAPI request object for accessing headers and state.
        background_tasks: FastAPI background tasks for async billing operations. user:
        Authenticated user with validated API key and sufficient balance.

        Returns: ChatCompletion: OpenAI-compatible completion response with usage data.

        Raises: HTTPException: - 401 if authentication fails or insufficient balance. -
        400 if request validation fails. - 500 if internal processing error occurs.

        Billing: - Token usage billed automatically based on model pricing - MCP tool
        calls billed separately using credits system - Streaming responses billed after
        completion via background task

        Example: Basic chat completion: ```python from dedalus_labs import Dedalus

            client = Dedalus(api_key="your-api-key")

            completion = client.chat.completions.create(
                model="openai/gpt-5",
                messages=[{"role": "user", "content": "Hello, how are you?"}],
            )

            print(completion.choices[0].message.content)
            ```

            With tools and MCP servers:
            ```python
            completion = client.chat.completions.create(
                model="openai/gpt-5",
                messages=[{"role": "user", "content": "Search for recent AI news"}],
                tools=[
                    {
                        "type": "function",
                        "function": {
                            "name": "search_web",
                            "description": "Search the web for information",
                        },
                    }
                ],
                mcp_servers=["dedalus-labs/brave-search"],
            )
            ```

            Multi-model routing:
            ```python
            completion = client.chat.completions.create(
                model=[
                    "openai/gpt-4o-mini",
                    "openai/gpt-5",
                    "anthropic/claude-sonnet-4-20250514",
                ],
                messages=[{"role": "user", "content": "Analyze this complex data"}],
                agent_attributes={"complexity": 0.8, "accuracy": 0.9},
            )
            ```

            Streaming response:
            ```python
            stream = client.chat.completions.create(
                model="openai/gpt-5",
                messages=[{"role": "user", "content": "Tell me a story"}],
                stream=True,
            )

            for chunk in stream:
                if chunk.choices[0].delta.content:
                    print(chunk.choices[0].delta.content, end="")
            ```

        Args:
          messages: Conversation history. Accepts either a list of message objects or a string,
              which is treated as a single user message.

          model: Model(s) to use for completion. Can be a single model ID, a DedalusModel object,
              or a list for multi-model routing. Single model: 'openai/gpt-4',
              'anthropic/claude-3-5-sonnet-20241022', 'openai/gpt-4o-mini', or a DedalusModel
              instance. Multi-model routing: ['openai/gpt-4o-mini', 'openai/gpt-4',
              'anthropic/claude-3-5-sonnet'] or list of DedalusModel objects - agent will
              choose optimal model based on task complexity.

          stream: If true, the model response data is streamed to the client as it is generated
              using Server-Sent Events.

          agent_attributes: Attributes for the agent itself, influencing behavior and model selection.
              Format: {'attribute': value}, where values are 0.0-1.0. Common attributes:
              'complexity', 'accuracy', 'efficiency', 'creativity', 'friendliness'. Higher
              values indicate stronger preference for that characteristic.

          audio: Parameters for audio output. Required when requesting audio responses (for
              example, modalities including 'audio').

          disable_automatic_function_calling: Google-only flag to disable the SDK's automatic function execution. When true,
              the model returns function calls for the client to execute manually.

          frequency_penalty: Number between -2.0 and 2.0. Positive values penalize new tokens based on their
              existing frequency in the text so far, decreasing the model's likelihood to
              repeat the same line verbatim.

          function_call: Deprecated in favor of 'tool_choice'. Controls which function is called by the
              model (none, auto, or specific name).

          functions: Deprecated in favor of 'tools'. Legacy list of function definitions the model
              may generate JSON inputs for.

          generation_config: Google generationConfig object. Merged with auto-generated config. Use for
              Google-specific params (candidateCount, responseMimeType, etc.).

          guardrails: Guardrails to apply to the agent for input/output validation and safety checks.
              Reserved for future use - guardrails configuration format not yet finalized.

          handoff_config: Configuration for multi-model handoffs and agent orchestration. Reserved for
              future use - handoff configuration format not yet finalized.

          input: Convenience alias for Responses-style `input`. Used when `messages` is omitted
              to provide the user prompt directly.

          instructions: Convenience alias for Responses-style `instructions`. Takes precedence over
              `system` and over system-role messages when provided.

          logit_bias: Modify the likelihood of specified tokens appearing in the completion. Accepts a
              JSON object mapping token IDs (as strings) to bias values from -100 to 100. The
              bias is added to the logits before sampling; values between -1 and 1 nudge
              selection probability, while values like -100 or 100 effectively ban or require
              a token.

          logprobs: Whether to return log probabilities of the output tokens. If true, returns the
              log probabilities for each token in the response content.

          max_completion_tokens: An upper bound for the number of tokens that can be generated for a completion,
              including visible output and reasoning tokens.

          max_tokens: The maximum number of tokens that can be generated in the chat completion. This
              value can be used to control costs for text generated via API. This value is now
              deprecated in favor of 'max_completion_tokens' and is not compatible with
              o-series models.

          max_turns: Maximum number of turns for agent execution before terminating (default: 10).
              Each turn represents one model inference cycle. Higher values allow more complex
              reasoning but increase cost and latency.

          mcp_servers: MCP (Model Context Protocol) server addresses to make available for server-side
              tool execution. Entries can be URLs (e.g., 'https://mcp.example.com'), slugs
              (e.g., 'dedalus-labs/brave-search'), or structured objects specifying
              slug/version/url. MCP tools are executed server-side and billed separately.

          metadata: Set of up to 16 key-value string pairs that can be attached to the request for
              structured metadata.

          modalities: Output types you would like the model to generate. Most models default to
              ['text']; some support ['text', 'audio'].

          model_attributes: Attributes for individual models used in routing decisions during multi-model
              execution. Format: {'model_name': {'attribute': value}}, where values are
              0.0-1.0. Common attributes: 'intelligence', 'speed', 'cost', 'creativity',
              'accuracy'. Used by agent to select optimal model based on task requirements.

          n: How many chat completion choices to generate for each input message. Keep 'n' as
              1 to minimize costs.

          parallel_tool_calls: Whether to enable parallel function calling during tool use.

          prediction: Configuration for predicted outputs. Improves response times when you already
              know large portions of the response content.

          presence_penalty: Number between -2.0 and 2.0. Positive values penalize new tokens based on
              whether they appear in the text so far, increasing the model's likelihood to
              talk about new topics.

          prompt_cache_key: Used by OpenAI to cache responses for similar requests and optimize cache hit
              rates. Replaces the legacy 'user' field for caching.

          reasoning_effort: Constrains effort on reasoning for supported reasoning models. Higher values use
              more compute, potentially improving reasoning quality at the cost of latency and
              tokens.

          response_format:
              An object specifying the format that the model must output. Use {'type':
              'json_schema', 'json_schema': {...}} for structured outputs or {'type':
              'json_object'} for the legacy JSON mode. Currently only OpenAI-prefixed models
              honour this field; Anthropic and Google requests will return an
              invalid_request_error if it is supplied.

          safety_identifier: Stable identifier used to help detect users who might violate OpenAI usage
              policies. Consider hashing end-user identifiers before sending.

          safety_settings: Google safety settings (harm categories and thresholds).

          seed: If specified, system will make a best effort to sample deterministically.
              Determinism is not guaranteed for the same seed across different models or API
              versions.

          service_tier: Specifies the processing tier used for the request. 'auto' uses project
              defaults, while 'default' forces standard pricing and performance.

          stop: Not supported with latest reasoning models 'o3' and 'o4-mini'.

                      Up to 4 sequences where the API will stop generating further tokens; the returned text will not contain the stop sequence.

          store: Whether to store the output of this chat completion request for OpenAI model
              distillation or eval products. Image inputs over 8MB are dropped if storage is
              enabled.

          stream_options: Options for streaming responses. Only set when 'stream' is true (supports
              'include_usage' and 'include_obfuscation').

          system: System prompt/instructions. Anthropic: pass-through. Google: converted to
              systemInstruction. OpenAI: extracted from messages.

          temperature: What sampling temperature to use, between 0 and 2. Higher values like 0.8 make
              the output more random, while lower values like 0.2 make it more focused and
              deterministic. We generally recommend altering this or 'top_p' but not both.

          thinking: Extended thinking configuration (Anthropic only). Enables thinking blocks
              showing reasoning process. Requires min 1,024 token budget.

          tool_choice: Controls which (if any) tool is called by the model. 'none' stops tool calling,
              'auto' lets the model decide, and 'required' forces at least one tool
              invocation. Specific tool payloads force that tool.

          tool_config: Google tool configuration (function calling mode, etc.).

          tools: A list of tools the model may call. Supports OpenAI function tools and custom
              tools; use 'mcp_servers' for Dedalus-managed server-side tools.

          top_k: Top-k sampling. Anthropic: pass-through. Google: injected into
              generationConfig.topK.

          top_logprobs: An integer between 0 and 20 specifying how many of the most likely tokens to
              return at each position, with log probabilities. Requires 'logprobs' to be true.

          top_p: An alternative to sampling with temperature, called nucleus sampling, where the
              model considers the results of the tokens with top_p probability mass. So 0.1
              means only the tokens comprising the top 10% probability mass are considered. We
              generally recommend altering this or 'temperature' but not both.

          user: Stable identifier for your end-users. Helps OpenAI detect and prevent abuse and
              may boost cache hit rates. This field is being replaced by 'safety_identifier'
              and 'prompt_cache_key'.

          verbosity: Constrains the verbosity of the model's response. Lower values produce concise
              answers, higher values allow more detail.

          web_search_options: Configuration for OpenAI's web search tool. Learn more at
              https://platform.openai.com/docs/guides/tools-web-search?api-mode=chat.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds

          idempotency_key: Specify a custom idempotency key for this request
        """
        ...

    @overload
    async def create(
        self,
        *,
        messages: Union[Iterable[Dict[str, object]], str],
        model: completion_create_params.Model,
        stream: bool,
        agent_attributes: Optional[Dict[str, float]] | Omit = omit,
        audio: Optional[Dict[str, object]] | Omit = omit,
        disable_automatic_function_calling: Optional[bool] | Omit = omit,
        frequency_penalty: Optional[float] | Omit = omit,
        function_call: Union[str, Dict[str, object], None] | Omit = omit,
        functions: Optional[Iterable[Dict[str, object]]] | Omit = omit,
        generation_config: Optional[Dict[str, object]] | Omit = omit,
        guardrails: Optional[Iterable[Dict[str, object]]] | Omit = omit,
        handoff_config: Optional[Dict[str, object]] | Omit = omit,
        input: Union[Iterable[Dict[str, object]], str, None] | Omit = omit,
        instructions: Union[str, Iterable[Dict[str, object]], None] | Omit = omit,
        logit_bias: Optional[Dict[str, int]] | Omit = omit,
        logprobs: Optional[bool] | Omit = omit,
        max_completion_tokens: Optional[int] | Omit = omit,
        max_tokens: Optional[int] | Omit = omit,
        max_turns: Optional[int] | Omit = omit,
        mcp_servers: Optional[completion_create_params.MCPServers] | Omit = omit,
        metadata: Optional[Dict[str, str]] | Omit = omit,
        modalities: Optional[SequenceNotStr[str]] | Omit = omit,
        model_attributes: Optional[Dict[str, Dict[str, float]]] | Omit = omit,
        n: Optional[int] | Omit = omit,
        parallel_tool_calls: Optional[bool] | Omit = omit,
        prediction: Optional[Dict[str, object]] | Omit = omit,
        presence_penalty: Optional[float] | Omit = omit,
        prompt_cache_key: Optional[str] | Omit = omit,
        reasoning_effort: Optional[Literal["low", "medium", "high"]] | Omit = omit,
        response_format: Optional[Dict[str, object]] | Omit = omit,
        safety_identifier: Optional[str] | Omit = omit,
        safety_settings: Optional[Iterable[Dict[str, object]]] | Omit = omit,
        seed: Optional[int] | Omit = omit,
        service_tier: Optional[Literal["auto", "default"]] | Omit = omit,
        stop: Optional[SequenceNotStr[str]] | Omit = omit,
        store: Optional[bool] | Omit = omit,
        stream_options: Optional[Dict[str, object]] | Omit = omit,
        system: Union[str, Iterable[Dict[str, object]], None] | Omit = omit,
        temperature: Optional[float] | Omit = omit,
        thinking: Optional[completion_create_params.Thinking] | Omit = omit,
        tool_choice: Union[str, Dict[str, object], None] | Omit = omit,
        tool_config: Optional[Dict[str, object]] | Omit = omit,
        tools: Optional[Iterable[Dict[str, object]]] | Omit = omit,
        top_k: Optional[int] | Omit = omit,
        top_logprobs: Optional[int] | Omit = omit,
        top_p: Optional[float] | Omit = omit,
        user: Optional[str] | Omit = omit,
        verbosity: Optional[Literal["low", "medium", "high"]] | Omit = omit,
        web_search_options: Optional[Dict[str, object]] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
        idempotency_key: str | None = None,
    ) -> StreamChunk | AsyncStream[StreamChunk]:
        """
        Create a chat completion.

        This endpoint provides a vendor-agnostic chat completions API that works with
        thousands of LLMs. It supports MCP integration, multi-model routing with
        intelligent agentic handoffs, client-side and server-side tool execution, and
        streaming and non-streaming responses.

        Args: request: Chat completion request with messages, model, and configuration.
        http_request: FastAPI request object for accessing headers and state.
        background_tasks: FastAPI background tasks for async billing operations. user:
        Authenticated user with validated API key and sufficient balance.

        Returns: ChatCompletion: OpenAI-compatible completion response with usage data.

        Raises: HTTPException: - 401 if authentication fails or insufficient balance. -
        400 if request validation fails. - 500 if internal processing error occurs.

        Billing: - Token usage billed automatically based on model pricing - MCP tool
        calls billed separately using credits system - Streaming responses billed after
        completion via background task

        Example: Basic chat completion: ```python from dedalus_labs import Dedalus

            client = Dedalus(api_key="your-api-key")

            completion = client.chat.completions.create(
                model="openai/gpt-5",
                messages=[{"role": "user", "content": "Hello, how are you?"}],
            )

            print(completion.choices[0].message.content)
            ```

            With tools and MCP servers:
            ```python
            completion = client.chat.completions.create(
                model="openai/gpt-5",
                messages=[{"role": "user", "content": "Search for recent AI news"}],
                tools=[
                    {
                        "type": "function",
                        "function": {
                            "name": "search_web",
                            "description": "Search the web for information",
                        },
                    }
                ],
                mcp_servers=["dedalus-labs/brave-search"],
            )
            ```

            Multi-model routing:
            ```python
            completion = client.chat.completions.create(
                model=[
                    "openai/gpt-4o-mini",
                    "openai/gpt-5",
                    "anthropic/claude-sonnet-4-20250514",
                ],
                messages=[{"role": "user", "content": "Analyze this complex data"}],
                agent_attributes={"complexity": 0.8, "accuracy": 0.9},
            )
            ```

            Streaming response:
            ```python
            stream = client.chat.completions.create(
                model="openai/gpt-5",
                messages=[{"role": "user", "content": "Tell me a story"}],
                stream=True,
            )

            for chunk in stream:
                if chunk.choices[0].delta.content:
                    print(chunk.choices[0].delta.content, end="")
            ```

        Args:
          messages: Conversation history. Accepts either a list of message objects or a string,
              which is treated as a single user message.

          model: Model(s) to use for completion. Can be a single model ID, a DedalusModel object,
              or a list for multi-model routing. Single model: 'openai/gpt-4',
              'anthropic/claude-3-5-sonnet-20241022', 'openai/gpt-4o-mini', or a DedalusModel
              instance. Multi-model routing: ['openai/gpt-4o-mini', 'openai/gpt-4',
              'anthropic/claude-3-5-sonnet'] or list of DedalusModel objects - agent will
              choose optimal model based on task complexity.

          stream: If true, the model response data is streamed to the client as it is generated
              using Server-Sent Events.

          agent_attributes: Attributes for the agent itself, influencing behavior and model selection.
              Format: {'attribute': value}, where values are 0.0-1.0. Common attributes:
              'complexity', 'accuracy', 'efficiency', 'creativity', 'friendliness'. Higher
              values indicate stronger preference for that characteristic.

          audio: Parameters for audio output. Required when requesting audio responses (for
              example, modalities including 'audio').

          disable_automatic_function_calling: Google-only flag to disable the SDK's automatic function execution. When true,
              the model returns function calls for the client to execute manually.

          frequency_penalty: Number between -2.0 and 2.0. Positive values penalize new tokens based on their
              existing frequency in the text so far, decreasing the model's likelihood to
              repeat the same line verbatim.

          function_call: Deprecated in favor of 'tool_choice'. Controls which function is called by the
              model (none, auto, or specific name).

          functions: Deprecated in favor of 'tools'. Legacy list of function definitions the model
              may generate JSON inputs for.

          generation_config: Google generationConfig object. Merged with auto-generated config. Use for
              Google-specific params (candidateCount, responseMimeType, etc.).

          guardrails: Guardrails to apply to the agent for input/output validation and safety checks.
              Reserved for future use - guardrails configuration format not yet finalized.

          handoff_config: Configuration for multi-model handoffs and agent orchestration. Reserved for
              future use - handoff configuration format not yet finalized.

          input: Convenience alias for Responses-style `input`. Used when `messages` is omitted
              to provide the user prompt directly.

          instructions: Convenience alias for Responses-style `instructions`. Takes precedence over
              `system` and over system-role messages when provided.

          logit_bias: Modify the likelihood of specified tokens appearing in the completion. Accepts a
              JSON object mapping token IDs (as strings) to bias values from -100 to 100. The
              bias is added to the logits before sampling; values between -1 and 1 nudge
              selection probability, while values like -100 or 100 effectively ban or require
              a token.

          logprobs: Whether to return log probabilities of the output tokens. If true, returns the
              log probabilities for each token in the response content.

          max_completion_tokens: An upper bound for the number of tokens that can be generated for a completion,
              including visible output and reasoning tokens.

          max_tokens: The maximum number of tokens that can be generated in the chat completion. This
              value can be used to control costs for text generated via API. This value is now
              deprecated in favor of 'max_completion_tokens' and is not compatible with
              o-series models.

          max_turns: Maximum number of turns for agent execution before terminating (default: 10).
              Each turn represents one model inference cycle. Higher values allow more complex
              reasoning but increase cost and latency.

          mcp_servers: MCP (Model Context Protocol) server addresses to make available for server-side
              tool execution. Entries can be URLs (e.g., 'https://mcp.example.com'), slugs
              (e.g., 'dedalus-labs/brave-search'), or structured objects specifying
              slug/version/url. MCP tools are executed server-side and billed separately.

          metadata: Set of up to 16 key-value string pairs that can be attached to the request for
              structured metadata.

          modalities: Output types you would like the model to generate. Most models default to
              ['text']; some support ['text', 'audio'].

          model_attributes: Attributes for individual models used in routing decisions during multi-model
              execution. Format: {'model_name': {'attribute': value}}, where values are
              0.0-1.0. Common attributes: 'intelligence', 'speed', 'cost', 'creativity',
              'accuracy'. Used by agent to select optimal model based on task requirements.

          n: How many chat completion choices to generate for each input message. Keep 'n' as
              1 to minimize costs.

          parallel_tool_calls: Whether to enable parallel function calling during tool use.

          prediction: Configuration for predicted outputs. Improves response times when you already
              know large portions of the response content.

          presence_penalty: Number between -2.0 and 2.0. Positive values penalize new tokens based on
              whether they appear in the text so far, increasing the model's likelihood to
              talk about new topics.

          prompt_cache_key: Used by OpenAI to cache responses for similar requests and optimize cache hit
              rates. Replaces the legacy 'user' field for caching.

          reasoning_effort: Constrains effort on reasoning for supported reasoning models. Higher values use
              more compute, potentially improving reasoning quality at the cost of latency and
              tokens.

          response_format:
              An object specifying the format that the model must output. Use {'type':
              'json_schema', 'json_schema': {...}} for structured outputs or {'type':
              'json_object'} for the legacy JSON mode. Currently only OpenAI-prefixed models
              honour this field; Anthropic and Google requests will return an
              invalid_request_error if it is supplied.

          safety_identifier: Stable identifier used to help detect users who might violate OpenAI usage
              policies. Consider hashing end-user identifiers before sending.

          safety_settings: Google safety settings (harm categories and thresholds).

          seed: If specified, system will make a best effort to sample deterministically.
              Determinism is not guaranteed for the same seed across different models or API
              versions.

          service_tier: Specifies the processing tier used for the request. 'auto' uses project
              defaults, while 'default' forces standard pricing and performance.

          stop: Not supported with latest reasoning models 'o3' and 'o4-mini'.

                      Up to 4 sequences where the API will stop generating further tokens; the returned text will not contain the stop sequence.

          store: Whether to store the output of this chat completion request for OpenAI model
              distillation or eval products. Image inputs over 8MB are dropped if storage is
              enabled.

          stream_options: Options for streaming responses. Only set when 'stream' is true (supports
              'include_usage' and 'include_obfuscation').

          system: System prompt/instructions. Anthropic: pass-through. Google: converted to
              systemInstruction. OpenAI: extracted from messages.

          temperature: What sampling temperature to use, between 0 and 2. Higher values like 0.8 make
              the output more random, while lower values like 0.2 make it more focused and
              deterministic. We generally recommend altering this or 'top_p' but not both.

          thinking: Extended thinking configuration (Anthropic only). Enables thinking blocks
              showing reasoning process. Requires min 1,024 token budget.

          tool_choice: Controls which (if any) tool is called by the model. 'none' stops tool calling,
              'auto' lets the model decide, and 'required' forces at least one tool
              invocation. Specific tool payloads force that tool.

          tool_config: Google tool configuration (function calling mode, etc.).

          tools: A list of tools the model may call. Supports OpenAI function tools and custom
              tools; use 'mcp_servers' for Dedalus-managed server-side tools.

          top_k: Top-k sampling. Anthropic: pass-through. Google: injected into
              generationConfig.topK.

          top_logprobs: An integer between 0 and 20 specifying how many of the most likely tokens to
              return at each position, with log probabilities. Requires 'logprobs' to be true.

          top_p: An alternative to sampling with temperature, called nucleus sampling, where the
              model considers the results of the tokens with top_p probability mass. So 0.1
              means only the tokens comprising the top 10% probability mass are considered. We
              generally recommend altering this or 'temperature' but not both.

          user: Stable identifier for your end-users. Helps OpenAI detect and prevent abuse and
              may boost cache hit rates. This field is being replaced by 'safety_identifier'
              and 'prompt_cache_key'.

          verbosity: Constrains the verbosity of the model's response. Lower values produce concise
              answers, higher values allow more detail.

          web_search_options: Configuration for OpenAI's web search tool. Learn more at
              https://platform.openai.com/docs/guides/tools-web-search?api-mode=chat.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds

          idempotency_key: Specify a custom idempotency key for this request
        """
        ...

    @required_args(["messages", "model"], ["messages", "model", "stream"])
    async def create(
        self,
        *,
        messages: Union[Iterable[Dict[str, object]], str],
        model: completion_create_params.Model,
        agent_attributes: Optional[Dict[str, float]] | Omit = omit,
        audio: Optional[Dict[str, object]] | Omit = omit,
        disable_automatic_function_calling: Optional[bool] | Omit = omit,
        frequency_penalty: Optional[float] | Omit = omit,
        function_call: Union[str, Dict[str, object], None] | Omit = omit,
        functions: Optional[Iterable[Dict[str, object]]] | Omit = omit,
        generation_config: Optional[Dict[str, object]] | Omit = omit,
        guardrails: Optional[Iterable[Dict[str, object]]] | Omit = omit,
        handoff_config: Optional[Dict[str, object]] | Omit = omit,
        input: Union[Iterable[Dict[str, object]], str, None] | Omit = omit,
        instructions: Union[str, Iterable[Dict[str, object]], None] | Omit = omit,
        logit_bias: Optional[Dict[str, int]] | Omit = omit,
        logprobs: Optional[bool] | Omit = omit,
        max_completion_tokens: Optional[int] | Omit = omit,
        max_tokens: Optional[int] | Omit = omit,
        max_turns: Optional[int] | Omit = omit,
        mcp_servers: Optional[completion_create_params.MCPServers] | Omit = omit,
        metadata: Optional[Dict[str, str]] | Omit = omit,
        modalities: Optional[SequenceNotStr[str]] | Omit = omit,
        model_attributes: Optional[Dict[str, Dict[str, float]]] | Omit = omit,
        n: Optional[int] | Omit = omit,
        parallel_tool_calls: Optional[bool] | Omit = omit,
        prediction: Optional[Dict[str, object]] | Omit = omit,
        presence_penalty: Optional[float] | Omit = omit,
        prompt_cache_key: Optional[str] | Omit = omit,
        reasoning_effort: Optional[Literal["low", "medium", "high"]] | Omit = omit,
        response_format: Optional[Dict[str, object]] | Omit = omit,
        safety_identifier: Optional[str] | Omit = omit,
        safety_settings: Optional[Iterable[Dict[str, object]]] | Omit = omit,
        seed: Optional[int] | Omit = omit,
        service_tier: Optional[Literal["auto", "default"]] | Omit = omit,
        stop: Optional[SequenceNotStr[str]] | Omit = omit,
        store: Optional[bool] | Omit = omit,
        stream: Literal[False] | Literal[True] | Omit = omit,
        stream_options: Optional[Dict[str, object]] | Omit = omit,
        system: Union[str, Iterable[Dict[str, object]], None] | Omit = omit,
        temperature: Optional[float] | Omit = omit,
        thinking: Optional[completion_create_params.Thinking] | Omit = omit,
        tool_choice: Union[str, Dict[str, object], None] | Omit = omit,
        tool_config: Optional[Dict[str, object]] | Omit = omit,
        tools: Optional[Iterable[Dict[str, object]]] | Omit = omit,
        top_k: Optional[int] | Omit = omit,
        top_logprobs: Optional[int] | Omit = omit,
        top_p: Optional[float] | Omit = omit,
        user: Optional[str] | Omit = omit,
        verbosity: Optional[Literal["low", "medium", "high"]] | Omit = omit,
        web_search_options: Optional[Dict[str, object]] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
        idempotency_key: str | None = None,
    ) -> StreamChunk | AsyncStream[StreamChunk]:
        return await self._post(
            "/v1/chat/completions",
            body=await async_maybe_transform(
                {
                    "messages": messages,
                    "model": model,
                    "agent_attributes": agent_attributes,
                    "audio": audio,
                    "disable_automatic_function_calling": disable_automatic_function_calling,
                    "frequency_penalty": frequency_penalty,
                    "function_call": function_call,
                    "functions": functions,
                    "generation_config": generation_config,
                    "guardrails": guardrails,
                    "handoff_config": handoff_config,
                    "input": input,
                    "instructions": instructions,
                    "logit_bias": logit_bias,
                    "logprobs": logprobs,
                    "max_completion_tokens": max_completion_tokens,
                    "max_tokens": max_tokens,
                    "max_turns": max_turns,
                    "mcp_servers": mcp_servers,
                    "metadata": metadata,
                    "modalities": modalities,
                    "model_attributes": model_attributes,
                    "n": n,
                    "parallel_tool_calls": parallel_tool_calls,
                    "prediction": prediction,
                    "presence_penalty": presence_penalty,
                    "prompt_cache_key": prompt_cache_key,
                    "reasoning_effort": reasoning_effort,
                    "response_format": response_format,
                    "safety_identifier": safety_identifier,
                    "safety_settings": safety_settings,
                    "seed": seed,
                    "service_tier": service_tier,
                    "stop": stop,
                    "store": store,
                    "stream": stream,
                    "stream_options": stream_options,
                    "system": system,
                    "temperature": temperature,
                    "thinking": thinking,
                    "tool_choice": tool_choice,
                    "tool_config": tool_config,
                    "tools": tools,
                    "top_k": top_k,
                    "top_logprobs": top_logprobs,
                    "top_p": top_p,
                    "user": user,
                    "verbosity": verbosity,
                    "web_search_options": web_search_options,
                },
                completion_create_params.CompletionCreateParamsStreaming
                if stream
                else completion_create_params.CompletionCreateParamsNonStreaming,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
            ),
            cast_to=StreamChunk,
            stream=stream or False,
            stream_cls=AsyncStream[StreamChunk],
        )


class CompletionsResourceWithRawResponse:
    def __init__(self, completions: CompletionsResource) -> None:
        self._completions = completions

        self.create = to_raw_response_wrapper(
            completions.create,
        )


class AsyncCompletionsResourceWithRawResponse:
    def __init__(self, completions: AsyncCompletionsResource) -> None:
        self._completions = completions

        self.create = async_to_raw_response_wrapper(
            completions.create,
        )


class CompletionsResourceWithStreamingResponse:
    def __init__(self, completions: CompletionsResource) -> None:
        self._completions = completions

        self.create = to_streamed_response_wrapper(
            completions.create,
        )


class AsyncCompletionsResourceWithStreamingResponse:
    def __init__(self, completions: AsyncCompletionsResource) -> None:
        self._completions = completions

        self.create = async_to_streamed_response_wrapper(
            completions.create,
        )
