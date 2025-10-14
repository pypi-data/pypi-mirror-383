# mix-python-sdk

Developer-friendly & type-safe Python SDK specifically catered to leverage *mix-python-sdk* API.

<div align="left">
    <a href="https://www.speakeasy.com/?utm_source=mix-python-sdk&utm_campaign=python"><img src="https://www.speakeasy.com/assets/badges/built-by-speakeasy.svg" /></a>
    <a href="https://opensource.org/licenses/MIT">
        <img src="https://img.shields.io/badge/License-MIT-blue.svg" style="width: 100px; height: 28px;" />
    </a>
</div>

<br /><br />

<!-- Start Summary [summary] -->
## Summary

Mix REST API: REST API for the Mix application - session management, messaging, and system operations
<!-- End Summary [summary] -->

<!-- Start Table of Contents [toc] -->
## Table of Contents
<!-- $toc-max-depth=2 -->
* [mix-python-sdk](#mix-python-sdk)
  * [SDK Installation](#sdk-installation)
  * [IDE Support](#ide-support)
  * [Quick Start](#quick-start)
  * [SDK Example Usage](#sdk-example-usage)
  * [Available Resources and Operations](#available-resources-and-operations)
  * [Server-sent event streaming](#server-sent-event-streaming)
  * [File uploads](#file-uploads)
  * [Retries](#retries)
  * [Error Handling](#error-handling)
  * [Server Selection](#server-selection)
  * [Custom HTTP Client](#custom-http-client)
  * [Resource Management](#resource-management)
  * [Debugging](#debugging)
* [Development](#development)
  * [Maturity](#maturity)
  * [Contributions](#contributions)

<!-- End Table of Contents [toc] -->

<!-- Start SDK Installation [installation] -->
## SDK Installation

> [!NOTE]
> **Python version upgrade policy**
>
> Once a Python version reaches its [official end of life date](https://devguide.python.org/versions/), a 3-month grace period is provided for users to upgrade. Following this grace period, the minimum python version supported in the SDK will be updated.

The SDK can be installed with *uv*, *pip*, or *poetry* package managers.

### uv

*uv* is a fast Python package installer and resolver, designed as a drop-in replacement for pip and pip-tools. It's recommended for its speed and modern Python tooling capabilities.

```bash
uv add mix-python-sdk
```

### PIP

*PIP* is the default package installer for Python, enabling easy installation and management of packages from PyPI via the command line.

```bash
pip install mix-python-sdk
```

### Poetry

*Poetry* is a modern tool that simplifies dependency management and package publishing by using a single `pyproject.toml` file to handle project metadata and dependencies.

```bash
poetry add mix-python-sdk
```

### Shell and script usage with `uv`

You can use this SDK in a Python shell with [uv](https://docs.astral.sh/uv/) and the `uvx` command that comes with it like so:

```shell
uvx --from mix-python-sdk python
```

It's also possible to write a standalone Python script without needing to set up a whole project like so:

```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "mix-python-sdk",
# ]
# ///

from mix_python_sdk import Mix

sdk = Mix(
  # SDK arguments
)

# Rest of script here...
```

Once that is saved to a file, you can run it with `uv run script.py` where
`script.py` can be replaced with the actual file name.
<!-- End SDK Installation [installation] -->

<!-- Start IDE Support [idesupport] -->
## IDE Support

### PyCharm

Generally, the SDK will work well with most IDEs out of the box. However, when using PyCharm, you can enjoy much better integration with Pydantic by installing an additional plugin.

- [PyCharm Pydantic Plugin](https://docs.pydantic.dev/latest/integrations/pycharm/)
<!-- End IDE Support [idesupport] -->

## Quick Start

The Mix SDK provides high-level helper functions for common patterns like streaming interactions. Here are three simple ways to get started:

### 1. Callback-based Streaming (Recommended for Beginners)

```python
import asyncio
import os
from mix_python_sdk import Mix
from mix_python_sdk.helpers import send_with_callbacks

async def main():
    async with Mix(server_url="http://localhost:8088") as mix:
        mix.authentication.store_api_key(
            api_key=os.getenv("OPENROUTER_API_KEY"),
            provider="openrouter"
        )
        session = mix.sessions.create(title="Demo")

        await send_with_callbacks(
            mix,
            session_id=session.id,
            message="What's the weather?",
            on_content=lambda text: print(text, end="", flush=True),
            on_complete=lambda: print("\nDone!")
        )

asyncio.run(main())
```

### 2. Async Iterator Pattern

```python
from mix_python_sdk import Mix
from mix_python_sdk.helpers import query

async with Mix(server_url="http://localhost:8088") as mix:
    session = mix.sessions.create(title="Demo")

    async for event in query(mix, session.id, "Hello!"):
        if event.type == "content":
            print(event.content, end="", flush=True)
```

### 3. Session Context Manager

```python
from mix_python_sdk import Mix
from mix_python_sdk.helpers import StreamingSession

async with Mix(server_url="http://localhost:8088") as mix:
    async with StreamingSession(mix, title="Demo") as session:
        await session.send(
            "What's 2+2?",
            on_content=lambda text: print(text, end="", flush=True)
        )
```

See the [examples/](examples/) directory for complete working examples.

<!-- Start SDK Example Usage [usage] -->
## SDK Example Usage

### Example

```python
# Synchronous Example
from mix_python_sdk import Mix


with Mix() as mix:

    res = mix.authentication.store_api_key(api_key="<value>", provider="openrouter")

    # Handle response
    print(res)
```

</br>

The same SDK client can also be used to make asynchronous requests by importing asyncio.

```python
# Asynchronous Example
import asyncio
from mix_python_sdk import Mix

async def main():

    async with Mix() as mix:

        res = await mix.authentication.store_api_key_async(api_key="<value>", provider="openrouter")

        # Handle response
        print(res)

asyncio.run(main())
```
<!-- End SDK Example Usage [usage] -->

<!-- Start Available Resources and Operations [operations] -->
## Available Resources and Operations

<details open>
<summary>Available methods</summary>

### [authentication](docs/sdks/authentication/README.md)

* [store_api_key](docs/sdks/authentication/README.md#store_api_key) - Store API key
* [handle_o_auth_callback](docs/sdks/authentication/README.md#handle_o_auth_callback) - Handle OAuth callback
* [start_o_auth_flow](docs/sdks/authentication/README.md#start_o_auth_flow) - Start OAuth authentication
* [get_auth_status](docs/sdks/authentication/README.md#get_auth_status) - Get authentication status
* [validate_preferred_provider](docs/sdks/authentication/README.md#validate_preferred_provider) - Validate preferred provider
* [delete_credentials](docs/sdks/authentication/README.md#delete_credentials) - Delete provider credentials
* [get_o_auth_health](docs/sdks/authentication/README.md#get_o_auth_health) - Get OAuth authentication health
* [refresh_o_auth_tokens](docs/sdks/authentication/README.md#refresh_o_auth_tokens) - Manually refresh OAuth tokens

### [files](docs/sdks/files/README.md)

* [list_session_files](docs/sdks/files/README.md#list_session_files) - List session files
* [upload_session_file](docs/sdks/files/README.md#upload_session_file) - Upload file to session
* [delete_session_file](docs/sdks/files/README.md#delete_session_file) - Delete session file
* [get_session_file](docs/sdks/files/README.md#get_session_file) - Get session file

### [health](docs/sdks/health/README.md)

* [get_o_auth_health](docs/sdks/health/README.md#get_o_auth_health) - Get OAuth authentication health

### [internal](docs/sdks/internal/README.md)

* [refresh_o_auth_tokens](docs/sdks/internal/README.md#refresh_o_auth_tokens) - Manually refresh OAuth tokens

### [messages](docs/sdks/messages/README.md)

* [get_history](docs/sdks/messages/README.md#get_history) - Get global message history
* [list_session](docs/sdks/messages/README.md#list_session) - List session messages
* [send](docs/sdks/messages/README.md#send) - Send a message to session (async)

### [permissions](docs/sdks/permissions/README.md)

* [deny](docs/sdks/permissions/README.md#deny) - Deny permission
* [grant](docs/sdks/permissions/README.md#grant) - Grant permission

### [preferences](docs/sdks/preferencessdk/README.md)

* [get_preferences](docs/sdks/preferencessdk/README.md#get_preferences) - Get user preferences
* [update_preferences](docs/sdks/preferencessdk/README.md#update_preferences) - Update user preferences
* [get_available_providers](docs/sdks/preferencessdk/README.md#get_available_providers) - Get available providers
* [reset_preferences](docs/sdks/preferencessdk/README.md#reset_preferences) - Reset preferences

### [sessions](docs/sdks/sessions/README.md)

* [list](docs/sdks/sessions/README.md#list) - List all sessions
* [create](docs/sdks/sessions/README.md#create) - Create a new session
* [delete](docs/sdks/sessions/README.md#delete) - Delete a session
* [get](docs/sdks/sessions/README.md#get) - Get a specific session
* [export_session](docs/sdks/sessions/README.md#export_session) - Export session transcript
* [fork](docs/sdks/sessions/README.md#fork) - Fork a session
* [rewind_session](docs/sdks/sessions/README.md#rewind_session) - Rewind a session
* [cancel_processing](docs/sdks/sessions/README.md#cancel_processing) - Cancel agent processing

### [streaming](docs/sdks/streaming/README.md)

* [stream_events](docs/sdks/streaming/README.md#stream_events) - Server-Sent Events stream for real-time updates

### [system](docs/sdks/system/README.md)

* [list_commands](docs/sdks/system/README.md#list_commands) - List available commands
* [get_command](docs/sdks/system/README.md#get_command) - Get specific command
* [list_mcp_servers](docs/sdks/system/README.md#list_mcp_servers) - List MCP servers
* [get_system_info](docs/sdks/system/README.md#get_system_info) - Get system information
* [get_health](docs/sdks/system/README.md#get_health) - Health check

### [tools](docs/sdks/tools/README.md)

* [get_tools_status](docs/sdks/tools/README.md#get_tools_status) - Get tools status

</details>
<!-- End Available Resources and Operations [operations] -->

<!-- Start Server-sent event streaming [eventstream] -->
## Server-sent event streaming

[Server-sent events][mdn-sse] are used to stream content from certain
operations. These operations will expose the stream as [Generator][generator] that
can be consumed using a simple `for` loop. The loop will
terminate when the server no longer has any events to send and closes the
underlying connection.  

The stream is also a [Context Manager][context-manager] and can be used with the `with` statement and will close the
underlying connection when the context is exited.

```python
from mix_python_sdk import Mix


with Mix() as mix:

    res = mix.streaming.stream_events(session_id="<id>")

    with res as event_stream:
        for event in event_stream:
            # handle event
            print(event, flush=True)

```

[mdn-sse]: https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events
[generator]: https://book.pythontips.com/en/latest/generators.html
[context-manager]: https://book.pythontips.com/en/latest/context_managers.html
<!-- End Server-sent event streaming [eventstream] -->

<!-- Start File uploads [file-upload] -->
## File uploads

Certain SDK methods accept file objects as part of a request body or multi-part request. It is possible and typically recommended to upload files as a stream rather than reading the entire contents into memory. This avoids excessive memory consumption and potentially crashing with out-of-memory errors when working with very large files. The following example demonstrates how to attach a file stream to a request.

> [!TIP]
>
> For endpoints that handle file uploads bytes arrays can also be used. However, using streams is recommended for large files.
>

```python
from mix_python_sdk import Mix


with Mix() as mix:

    res = mix.files.upload_session_file(id="<id>", file={
        "file_name": "example.file",
        "content": open("example.file", "rb"),
    })

    # Handle response
    print(res)

```
<!-- End File uploads [file-upload] -->

<!-- Start Retries [retries] -->
## Retries

Some of the endpoints in this SDK support retries. If you use the SDK without any configuration, it will fall back to the default retry strategy provided by the API. However, the default retry strategy can be overridden on a per-operation basis, or across the entire SDK.

To change the default retry strategy for a single API call, simply provide a `RetryConfig` object to the call:
```python
from mix_python_sdk import Mix
from mix_python_sdk.utils import BackoffStrategy, RetryConfig


with Mix() as mix:

    res = mix.authentication.store_api_key(api_key="<value>", provider="openrouter",
        RetryConfig("backoff", BackoffStrategy(1, 50, 1.1, 100), False))

    # Handle response
    print(res)

```

If you'd like to override the default retry strategy for all operations that support retries, you can use the `retry_config` optional parameter when initializing the SDK:
```python
from mix_python_sdk import Mix
from mix_python_sdk.utils import BackoffStrategy, RetryConfig


with Mix(
    retry_config=RetryConfig("backoff", BackoffStrategy(1, 50, 1.1, 100), False),
) as mix:

    res = mix.authentication.store_api_key(api_key="<value>", provider="openrouter")

    # Handle response
    print(res)

```
<!-- End Retries [retries] -->

<!-- Start Error Handling [errors] -->
## Error Handling

[`MixError`](./src/mix_python_sdk/errors/mixerror.py) is the base class for all HTTP error responses. It has the following properties:

| Property           | Type             | Description                                                                             |
| ------------------ | ---------------- | --------------------------------------------------------------------------------------- |
| `err.message`      | `str`            | Error message                                                                           |
| `err.status_code`  | `int`            | HTTP response status code eg `404`                                                      |
| `err.headers`      | `httpx.Headers`  | HTTP response headers                                                                   |
| `err.body`         | `str`            | HTTP body. Can be empty string if no body is returned.                                  |
| `err.raw_response` | `httpx.Response` | Raw HTTP response                                                                       |
| `err.data`         |                  | Optional. Some errors may contain structured data. [See Error Classes](#error-classes). |

### Example
```python
from mix_python_sdk import Mix, errors


with Mix() as mix:
    res = None
    try:

        res = mix.authentication.store_api_key(api_key="<value>", provider="openrouter")

        # Handle response
        print(res)


    except errors.MixError as e:
        # The base class for HTTP error responses
        print(e.message)
        print(e.status_code)
        print(e.body)
        print(e.headers)
        print(e.raw_response)

        # Depending on the method different errors may be thrown
        if isinstance(e, errors.ErrorResponse):
            print(e.data.error)  # models.RESTError
```

### Error Classes
**Primary errors:**
* [`MixError`](./src/mix_python_sdk/errors/mixerror.py): The base class for HTTP error responses.
  * [`ErrorResponse`](./src/mix_python_sdk/errors/errorresponse.py): *

<details><summary>Less common errors (5)</summary>

<br />

**Network errors:**
* [`httpx.RequestError`](https://www.python-httpx.org/exceptions/#httpx.RequestError): Base class for request errors.
    * [`httpx.ConnectError`](https://www.python-httpx.org/exceptions/#httpx.ConnectError): HTTP client was unable to make a request to a server.
    * [`httpx.TimeoutException`](https://www.python-httpx.org/exceptions/#httpx.TimeoutException): HTTP request timed out.


**Inherit from [`MixError`](./src/mix_python_sdk/errors/mixerror.py)**:
* [`ResponseValidationError`](./src/mix_python_sdk/errors/responsevalidationerror.py): Type mismatch between the response data and the expected Pydantic model. Provides access to the Pydantic validation error via the `cause` attribute.

</details>

\* Check [the method documentation](#available-resources-and-operations) to see if the error is applicable.
<!-- End Error Handling [errors] -->

<!-- Start Server Selection [server] -->
## Server Selection

### Override Server URL Per-Client

The default server can be overridden globally by passing a URL to the `server_url: str` optional parameter when initializing the SDK client instance. For example:
```python
from mix_python_sdk import Mix


with Mix(
    server_url="http://localhost:8088",
) as mix:

    res = mix.authentication.store_api_key(api_key="<value>", provider="openrouter")

    # Handle response
    print(res)

```
<!-- End Server Selection [server] -->

<!-- Start Custom HTTP Client [http-client] -->
## Custom HTTP Client

The Python SDK makes API calls using the [httpx](https://www.python-httpx.org/) HTTP library.  In order to provide a convenient way to configure timeouts, cookies, proxies, custom headers, and other low-level configuration, you can initialize the SDK client with your own HTTP client instance.
Depending on whether you are using the sync or async version of the SDK, you can pass an instance of `HttpClient` or `AsyncHttpClient` respectively, which are Protocol's ensuring that the client has the necessary methods to make API calls.
This allows you to wrap the client with your own custom logic, such as adding custom headers, logging, or error handling, or you can just pass an instance of `httpx.Client` or `httpx.AsyncClient` directly.

For example, you could specify a header for every request that this sdk makes as follows:
```python
from mix_python_sdk import Mix
import httpx

http_client = httpx.Client(headers={"x-custom-header": "someValue"})
s = Mix(client=http_client)
```

or you could wrap the client with your own custom logic:
```python
from mix_python_sdk import Mix
from mix_python_sdk.httpclient import AsyncHttpClient
import httpx

class CustomClient(AsyncHttpClient):
    client: AsyncHttpClient

    def __init__(self, client: AsyncHttpClient):
        self.client = client

    async def send(
        self,
        request: httpx.Request,
        *,
        stream: bool = False,
        auth: Union[
            httpx._types.AuthTypes, httpx._client.UseClientDefault, None
        ] = httpx.USE_CLIENT_DEFAULT,
        follow_redirects: Union[
            bool, httpx._client.UseClientDefault
        ] = httpx.USE_CLIENT_DEFAULT,
    ) -> httpx.Response:
        request.headers["Client-Level-Header"] = "added by client"

        return await self.client.send(
            request, stream=stream, auth=auth, follow_redirects=follow_redirects
        )

    def build_request(
        self,
        method: str,
        url: httpx._types.URLTypes,
        *,
        content: Optional[httpx._types.RequestContent] = None,
        data: Optional[httpx._types.RequestData] = None,
        files: Optional[httpx._types.RequestFiles] = None,
        json: Optional[Any] = None,
        params: Optional[httpx._types.QueryParamTypes] = None,
        headers: Optional[httpx._types.HeaderTypes] = None,
        cookies: Optional[httpx._types.CookieTypes] = None,
        timeout: Union[
            httpx._types.TimeoutTypes, httpx._client.UseClientDefault
        ] = httpx.USE_CLIENT_DEFAULT,
        extensions: Optional[httpx._types.RequestExtensions] = None,
    ) -> httpx.Request:
        return self.client.build_request(
            method,
            url,
            content=content,
            data=data,
            files=files,
            json=json,
            params=params,
            headers=headers,
            cookies=cookies,
            timeout=timeout,
            extensions=extensions,
        )

s = Mix(async_client=CustomClient(httpx.AsyncClient()))
```
<!-- End Custom HTTP Client [http-client] -->

<!-- Start Resource Management [resource-management] -->
## Resource Management

The `Mix` class implements the context manager protocol and registers a finalizer function to close the underlying sync and async HTTPX clients it uses under the hood. This will close HTTP connections, release memory and free up other resources held by the SDK. In short-lived Python programs and notebooks that make a few SDK method calls, resource management may not be a concern. However, in longer-lived programs, it is beneficial to create a single SDK instance via a [context manager][context-manager] and reuse it across the application.

[context-manager]: https://docs.python.org/3/reference/datamodel.html#context-managers

```python
from mix_python_sdk import Mix
def main():

    with Mix() as mix:
        # Rest of application here...


# Or when using async:
async def amain():

    async with Mix() as mix:
        # Rest of application here...
```
<!-- End Resource Management [resource-management] -->

<!-- Start Debugging [debug] -->
## Debugging

You can setup your SDK to emit debug logs for SDK requests and responses.

You can pass your own logger class directly into your SDK.
```python
from mix_python_sdk import Mix
import logging

logging.basicConfig(level=logging.DEBUG)
s = Mix(debug_logger=logging.getLogger("mix_python_sdk"))
```

You can also enable a default debug logger by setting an environment variable `MIX_DEBUG` to true.
<!-- End Debugging [debug] -->

<!-- Placeholder for Future Speakeasy SDK Sections -->

# Development

## Maturity

This SDK is in beta, and there may be breaking changes between versions without a major version update. Therefore, we recommend pinning usage
to a specific package version. This way, you can install the same version each time without breaking changes unless you are intentionally
looking for the latest version.

## Contributions

While we value open-source contributions to this SDK, this library is generated programmatically. Any manual changes added to internal files will be overwritten on the next generation.
We look forward to hearing your feedback. Feel free to open a PR or an issue with a proof of concept and we'll do our best to include it in a future release.

### SDK Created by [Speakeasy](https://www.speakeasy.com/?utm_source=mix-python-sdk&utm_campaign=python)
