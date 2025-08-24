========================
CODE SNIPPETS
========================
TITLE: Running Examples
DESCRIPTION: Commands to make an example script executable and then run it.

SOURCE: https://github.com/openai/openai-python/blob/main/CONTRIBUTING.md#_snippet_3

LANGUAGE: sh
CODE:
```
$ chmod +x examples/<your-example>.py
$ ./examples/<your-example>.py
```

----------------------------------------

TITLE: Adding and Running Examples
DESCRIPTION: Steps to add a new Python example file and make it executable, allowing it to be run against the API.

SOURCE: https://github.com/openai/openai-python/blob/main/CONTRIBUTING.md#_snippet_2

LANGUAGE: python
CODE:
```
# add an example to examples/<your-example>.py

#!/usr/bin/env -S rye run python
…
```

----------------------------------------

TITLE: Building and Installing from Source
DESCRIPTION: Commands to build the Python package distributable files (wheel) and then install it locally.

SOURCE: https://github.com/openai/openai-python/blob/main/CONTRIBUTING.md#_snippet_5

LANGUAGE: sh
CODE:
```
# Build the package
$ rye build
# or
$ python -m build

# Install the wheel file
$ pip install ./path-to-wheel-file.whl
```

----------------------------------------

TITLE: Installing from Git
DESCRIPTION: Command to install the OpenAI Python library directly from its Git repository using pip.

SOURCE: https://github.com/openai/openai-python/blob/main/CONTRIBUTING.md#_snippet_4

LANGUAGE: sh
CODE:
```
$ pip install git+ssh://git@github.com/openai/openai-python.git
```

----------------------------------------

TITLE: Environment Setup without Rye
DESCRIPTION: Instructions for setting up the project environment using standard pip, including installing development dependencies.

SOURCE: https://github.com/openai/openai-python/blob/main/CONTRIBUTING.md#_snippet_1

LANGUAGE: sh
CODE:
```
$ pip install -r requirements-dev.lock
```

----------------------------------------

TITLE: Environment Setup with Rye
DESCRIPTION: Commands to bootstrap the project environment using Rye, including syncing dependencies and activating the virtual environment.

SOURCE: https://github.com/openai/openai-python/blob/main/CONTRIBUTING.md#_snippet_0

LANGUAGE: sh
CODE:
```
#!/usr/bin/env sh
$ ./scripts/bootstrap

# Or install Rye manually and run:
$ rye sync --all-features

# Activate the virtual environment
$ source .venv/bin/activate

# Run scripts
$ python script.py
```

----------------------------------------

TITLE: Install OpenAI Library
DESCRIPTION: Installs the OpenAI Python library from PyPI using pip.

SOURCE: https://github.com/openai/openai-python/blob/main/README.md#_snippet_0

LANGUAGE: sh
CODE:
```
# install from PyPI
pip install openai
```

----------------------------------------

TITLE: Install aiohttp for Async Client
DESCRIPTION: Installs the `aiohttp` library, which can be used as an alternative backend for the asynchronous OpenAI client for improved concurrency.

SOURCE: https://github.com/openai/openai-python/blob/main/README.md#_snippet_6

LANGUAGE: sh
CODE:
```
pip install aiohttp
```

----------------------------------------

TITLE: Setting up Mock Server for Tests
DESCRIPTION: Instructions to set up a mock server using Prism for running tests against the OpenAPI specification.

SOURCE: https://github.com/openai/openai-python/blob/main/CONTRIBUTING.md#_snippet_6

LANGUAGE: sh
CODE:
```
# Requires npm installed
$ npx prism mock path/to/your/openapi.yml
```

----------------------------------------

TITLE: Manual Publishing to PyPI
DESCRIPTION: Instructions for manually publishing the package to PyPI using a provided script and environment variable.

SOURCE: https://github.com/openai/openai-python/blob/main/CONTRIBUTING.md#_snippet_9

LANGUAGE: sh
CODE:
```
# Ensure PYPI_TOKEN is set in the environment
$ bin/publish-pypi
```

----------------------------------------

TITLE: Install OpenAI with aiohttp
DESCRIPTION: Installs the OpenAI Python library with support for aiohttp, enabling asynchronous HTTP requests.

SOURCE: https://github.com/openai/openai-python/blob/main/README.md#_snippet_7

LANGUAGE: bash
CODE:
```
pip install openai[aiohttp]
```

----------------------------------------

TITLE: Linting and Formatting Code
DESCRIPTION: Commands to run linting checks and automatically format the code using Ruff and Black.

SOURCE: https://github.com/openai/openai-python/blob/main/CONTRIBUTING.md#_snippet_8

LANGUAGE: sh
CODE:
```
# To lint:
$ ./scripts/lint

# To format and fix issues:
$ ./scripts/format
```

----------------------------------------

TITLE: Running Project Tests
DESCRIPTION: Command to execute the project's test suite.

SOURCE: https://github.com/openai/openai-python/blob/main/CONTRIBUTING.md#_snippet_7

LANGUAGE: sh
CODE:
```
$ ./scripts/test
```

----------------------------------------

TITLE: Realtime API Basic Text Example
DESCRIPTION: Provides a basic example of using the Realtime API for text-based conversations. It connects to the API, updates modalities, sends a message, and processes text responses.

SOURCE: https://github.com/openai/openai-python/blob/main/README.md#_snippet_11

LANGUAGE: python
CODE:
```
import asyncio
from openai import AsyncOpenAI

async def main():
    client = AsyncOpenAI()

    async with client.beta.realtime.connect(model="gpt-4o-realtime-preview") as connection:
        await connection.session.update(session={'modalities': ['text']})

        await connection.conversation.item.create(
            item={
                "type": "message",
                "role": "user",
                "content": [{"type": "input_text", "text": "Say hello!"}],
            }
        )
        await connection.response.create()

        async for event in connection:
            if event.type == 'response.text.delta':
                print(event.delta, flush=True, end="")

            elif event.type == 'response.text.done':
                print()

            elif event.type == "response.done":
                break

asyncio.run(main())
```

----------------------------------------

TITLE: Async Usage Example
DESCRIPTION: Demonstrates asynchronous usage of the OpenAI client by importing `AsyncOpenAI` and using `await` for API calls. It includes running an async function with `asyncio.run`.

SOURCE: https://github.com/openai/openai-python/blob/main/README.md#_snippet_5

LANGUAGE: python
CODE:
```
import os
import asyncio
from openai import AsyncOpenAI

client = AsyncOpenAI(
    # This is the default and can be omitted
    api_key=os.environ.get("OPENAI_API_KEY"),
)


async def main() -> None:
    response = await client.responses.create(
        model="gpt-4o", input="Explain disestablishmentarianism to a smart five year old."
    )
    print(response.output_text)

asyncio.run(main())
```

----------------------------------------

TITLE: Azure OpenAI Client Initialization
DESCRIPTION: Provides an example of initializing the `AzureOpenAI` client for use with Azure OpenAI services, including specifying the API version and endpoint.

SOURCE: https://github.com/openai/openai-python/blob/main/README.md#_snippet_36

LANGUAGE: python
CODE:
```
from openai import AzureOpenAI

# gets the API Key from environment variable AZURE_OPENAI_API_KEY
client = AzureOpenAI(
    # https://learn.microsoft.com/azure/ai-services/openai/reference#rest-api-versioning
    api_version="2023-07-01-preview",
    # https://learn.microsoft.com/azure/cognitive-services/openai/how-to/create-resource?pivots=web-portal#create-a-resource
    azure_endpoint="https://example-endpoint.openai.azure.com",
)

completion = client.chat.completions.create(
    model="deployment-name",  # e.g. gpt-35-instant
    messages=[
        {
            "role": "user",
            "content": "How do I output all files in a directory using Python?",
        },
    ],
)
print(completion.to_json())
```

----------------------------------------

TITLE: Execute Project Tests
DESCRIPTION: This command runs the project's test suite. For most tests, a mock server (set up with `prism`) must be running against the OpenAPI specification for proper execution and validation.

SOURCE: https://github.com/openai/openai-python/blob/main/CONTRIBUTING.md#_snippet_10

LANGUAGE: sh
CODE:
```
./scripts/test
```

----------------------------------------

TITLE: Run Code Linting Checks
DESCRIPTION: This command executes the project's linting checks using configured tools like `ruff` and `black` to identify potential code quality, style, and best practice violations.

SOURCE: https://github.com/openai/openai-python/blob/main/CONTRIBUTING.md#_snippet_11

LANGUAGE: sh
CODE:
```
./scripts/lint
```

----------------------------------------

TITLE: Determine Installed OpenAI Version
DESCRIPTION: Shows how to check the currently installed version of the OpenAI Python package at runtime.

SOURCE: https://github.com/openai/openai-python/blob/main/README.md#_snippet_37

LANGUAGE: python
CODE:
```
import openai
print(openai.__version__)
```

----------------------------------------

TITLE: Run Code Formatting and Auto-Fix
DESCRIPTION: This command automatically formats the code and fixes `ruff` issues, ensuring adherence to the project's coding style guidelines using tools like `ruff` and `black` for consistent code appearance.

SOURCE: https://github.com/openai/openai-python/blob/main/CONTRIBUTING.md#_snippet_12

LANGUAGE: sh
CODE:
```
./scripts/format
```

----------------------------------------

TITLE: Webhook Verification and Payload Parsing
DESCRIPTION: Provides an example of how to verify webhook signatures and parse payloads using `client.webhooks.unwrap()`. It includes error handling for invalid signatures and demonstrates processing different event types.

SOURCE: https://github.com/openai/openai-python/blob/main/README.md#_snippet_19

LANGUAGE: python
CODE:
```
from openai import OpenAI
from flask import Flask, request

app = Flask(__name__)
client = OpenAI()  # OPENAI_WEBHOOK_SECRET environment variable is used by default


@app.route("/webhook", methods=["POST"])
def webhook():
    request_body = request.get_data(as_text=True)

    try:
        event = client.webhooks.unwrap(request_body, request.headers)

        if event.type == "response.completed":
            print("Response completed:", event.data)
        elif event.type == "response.failed":
            print("Response failed:", event.data)
        else:
            print("Unhandled event type:", event.type)

        return "ok"
    except Exception as e:
        print("Invalid signature:", e)
        return "Invalid signature", 400


if __name__ == "__main__":
    app.run(port=8000)
```

----------------------------------------

TITLE: Creating a Run for a Thread (OpenAI Python)
DESCRIPTION: This method initiates a new execution run for a specified `thread_id`. It accepts `params` to configure the run, such as the Assistant to use, and returns a `Run` object representing the newly started execution.

SOURCE: https://github.com/openai/openai-python/blob/main/api.md#_snippet_99

LANGUAGE: Python
CODE:
```
client.beta.threads.runs.create(thread_id, **params)
```

----------------------------------------

TITLE: Fix Package: Make Sounddevice and Numpy Optional Dependencies
DESCRIPTION: Modifies the package configuration to make `sounddevice` and `numpy` optional dependencies. This reduces the default installation footprint for users who do not require these specific functionalities.

SOURCE: https://github.com/openai/openai-python/blob/main/CHANGELOG.md#_snippet_25

LANGUAGE: APIDOC
CODE:
```
Bug Fix: Sounddevice and numpy made optional dependencies.
```

----------------------------------------

TITLE: Auto-parsing Function Tool Calls with Pydantic
DESCRIPTION: Illustrates how to automatically parse function tool calls using the `client.chat.completions.parse()` method in conjunction with `openai.pydantic_function_tool()`. This requires marking the tool schema with `"strict": True`. The example shows defining Pydantic models for table queries, conditions, and ordering, then using them to parse user requests into structured function calls.

SOURCE: https://github.com/openai/openai-python/blob/main/helpers.md#_snippet_1

LANGUAGE: python
CODE:
```
from enum import Enum
from typing import List, Union
from pydantic import BaseModel
import openai

class Table(str, Enum):
    orders = "orders"
    customers = "customers"
    products = "products"

class Column(str, Enum):
    id = "id"
    status = "status"
    expected_delivery_date = "expected_delivery_date"
    delivered_at = "delivered_at"
    shipped_at = "shipped_at"
    ordered_at = "ordered_at"
    canceled_at = "canceled_at"

class Operator(str, Enum):
    eq = "="
    gt = ">"
    lt = "<"
    le = "<="
    ge = ">="
    ne = "!="

class OrderBy(str, Enum):
    asc = "asc"
    desc = "desc"

class DynamicValue(BaseModel):
    column_name: str

class Condition(BaseModel):
    column: str
    operator: Operator
    value: Union[str, int, DynamicValue]

class Query(BaseModel):
    table_name: Table
    columns: List[Column]
    conditions: List[Condition]
    order_by: OrderBy

client = openai.OpenAI()
completion = client.chat.completions.parse(
    model="gpt-4o-2024-08-06",
    messages=[
        {
            "role": "system",
            "content": "You are a helpful assistant. The current date is August 6, 2024. You help users query for the data they are looking for by calling the query function.",
        },
        {
            "role": "user",
            "content": "look up all my orders in may of last year that were fulfilled but not delivered on time",
        },
    ],
    tools=[
        openai.pydantic_function_tool(Query),
    ],
)

tool_call = (completion.choices[0].message.tool_calls or [])[0]
print(tool_call.function)
assert isinstance(tool_call.function.parsed_arguments, Query)
print(tool_call.function.parsed_arguments.table_name)
```

----------------------------------------

TITLE: Creating and Streaming a Thread Run (OpenAI Python)
DESCRIPTION: This method creates a thread, starts a run, and streams real-time updates as the run progresses. It returns an `AssistantStreamManager` which allows for event-driven processing of the run's lifecycle.

SOURCE: https://github.com/openai/openai-python/blob/main/api.md#_snippet_97

LANGUAGE: Python
CODE:
```
client.beta.threads.create_and_run_stream(*args)
```

----------------------------------------

TITLE: Add API Endpoint: Get Chat Completions
DESCRIPTION: Adds a new API endpoint (`GET /chat/completions`) for retrieving chat completions. This provides a direct method to access chat completion results via the API.

SOURCE: https://github.com/openai/openai-python/blob/main/CHANGELOG.md#_snippet_17

LANGUAGE: APIDOC
CODE:
```
GET /chat/completions
```

----------------------------------------

TITLE: OpenAI Chat Completions API - Structured Outputs
DESCRIPTION: Details the OpenAI API's capability to extract JSON from model responses using the `response_format` parameter. This section references a guide for more in-depth information on the API itself. It highlights the SDK's `parse()` method as a wrapper for `create()` that enhances Python integration.

SOURCE: https://github.com/openai/openai-python/blob/main/helpers.md#_snippet_2

LANGUAGE: APIDOC
CODE:
```
OpenAI API:
  Chat Completions:
    response_format: object
      Allows extraction of JSON from the model response.
      See: https://platform.openai.com/docs/guides/structured-outputs

SDK Wrapper:
  client.chat.completions.parse()
    - Wrapper for client.chat.completions.create().
    - Provides richer integrations with Python types.
    - Returns a ParsedChatCompletion object (subclass of ChatCompletion).

Restrictions for .parse():
  - Raises LengthFinishReasonError or ContentFilterFinishReasonError if finish_reason is 'length' or 'content_filter'.
  - Only accepts strict function tools (e.g., {'type': 'function', 'function': {..., 'strict': True}}).
```

----------------------------------------

TITLE: OpenAI API Reference - Polling Helpers
DESCRIPTION: Helper functions provided by the SDK to poll asynchronous API actions until they reach a terminal state. These methods simplify the management of operations that take time to complete, such as starting runs or uploading files.

SOURCE: https://github.com/openai/openai-python/blob/main/helpers.md#_snippet_15

LANGUAGE: APIDOC
CODE:
```
Polling Helper Functions:

These functions poll the status of asynchronous operations until a terminal state is reached, returning the resulting object. They are indicated by methods ending in `_and_poll`.

- **Thread and Run Operations**:
  - `client.beta.threads.create_and_run_poll(...)`: Creates a thread and polls for run completion.
  - `client.beta.threads.runs.create_and_poll(...)`: Creates a run and polls for completion.
  - `client.beta.threads.runs.submit_tool_outputs_and_poll(...)`: Submits tool outputs for a run and polls for completion.

- **Vector Store Operations**:
  - `client.beta.vector_stores.files.upload_and_poll(...)`: Uploads a file to a vector store and polls for completion.
  - `client.beta.vector_stores.files.create_and_poll(...)`: Creates a file entry in a vector store and polls for completion.
  - `client.beta.vector_stores.file_batches.create_and_poll(...)`: Creates a file batch for a vector store and polls for completion.
  - `client.beta.vector_stores.file_batches.upload_and_poll(...)`: Uploads a file batch to a vector store and polls for completion.

*Polling Frequency*: The polling frequency can be controlled via the `poll_interval_ms` argument available in these methods.
```

----------------------------------------

TITLE: Add API Endpoint: Get Response Input Items
DESCRIPTION: Introduces a new API endpoint (`GET /responses/{response_id}/input_items`) to retrieve input items associated with a specific response ID. This enhances the ability to inspect the original data used for a given API response.

SOURCE: https://github.com/openai/openai-python/blob/main/CHANGELOG.md#_snippet_16

LANGUAGE: APIDOC
CODE:
```
GET /responses/{response_id}/input_items
```

----------------------------------------

TITLE: Creating and Polling a Thread Run (OpenAI Python)
DESCRIPTION: This method creates a thread, starts a run, and then synchronously polls for the run's completion. It's a convenience for blocking operations, returning the final `Run` object once execution finishes.

SOURCE: https://github.com/openai/openai-python/blob/main/api.md#_snippet_96

LANGUAGE: Python
CODE:
```
client.beta.threads.create_and_run_poll(*args)
```

----------------------------------------

TITLE: Async Client Initialization with aiohttp
DESCRIPTION: Demonstrates how to initialize the asynchronous OpenAI client using the DefaultAioHttpClient for making API calls.

SOURCE: https://github.com/openai/openai-python/blob/main/README.md#_snippet_8

LANGUAGE: python
CODE:
```
import asyncio
from openai import DefaultAioHttpClient
from openai import AsyncOpenAI


async def main() -> None:
    async with AsyncOpenAI(
        api_key="My API Key",
        http_client=DefaultAioHttpClient(),
    ) as client:
        chat_completion = await client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": "Say this is a test",
                }
            ],
            model="gpt-4o",
        )


asyncio.run(main())
```

----------------------------------------

TITLE: Creating Assistant API Streams
DESCRIPTION: Details the different methods available for initiating streaming responses with the Assistant API. These include streaming an existing run, creating a thread and running it, and streaming tool outputs.

SOURCE: https://github.com/openai/openai-python/blob/main/helpers.md#_snippet_9

LANGUAGE: python
CODE:
```
client.beta.threads.runs.stream()
```

LANGUAGE: python
CODE:
```
client.beta.threads.create_and_run_stream()
```

LANGUAGE: python
CODE:
```
client.beta.threads.runs.submit_tool_outputs_stream()
```

----------------------------------------

TITLE: Uploading Files for Fine-Tuning
DESCRIPTION: Demonstrates how to upload files for fine-tuning using the OpenAI client. It shows how to pass file contents as bytes, a PathLike object, or a tuple.

SOURCE: https://github.com/openai/openai-python/blob/main/README.md#_snippet_18

LANGUAGE: python
CODE:
```
from pathlib import Path
from openai import OpenAI

client = OpenAI()

client.files.create(
    file=Path("input.jsonl"),
    purpose="fine-tune",
)
```

----------------------------------------

TITLE: Configure HTTP Client with Proxies and Transports
DESCRIPTION: Demonstrates how to override the httpx client to include custom configurations like proxies and transports for the OpenAI Python client. This allows for advanced network configurations.

SOURCE: https://github.com/openai/openai-python/blob/main/README.md#_snippet_33

LANGUAGE: python
CODE:
```
import httpx
from openai import OpenAI, DefaultHttpxClient

client = OpenAI(
    # Or use the `OPENAI_BASE_URL` env var
    base_url="http://my.test.server.example.com:8083/v1",
    http_client=DefaultHttpxClient(
        proxy="http://my.test.proxy.example.com",
        transport=httpx.HTTPTransport(local_address="0.0.0.0"),
    ),
)
```

----------------------------------------

TITLE: Customize Client Per-Request
DESCRIPTION: Shows how to customize the HTTP client configuration on a per-request basis using the `with_options()` method.

SOURCE: https://github.com/openai/openai-python/blob/main/README.md#_snippet_34

LANGUAGE: python
CODE:
```
client.with_options(http_client=DefaultHttpxClient(...))
```

----------------------------------------

TITLE: OpenAI Client Configuration Options
DESCRIPTION: Lists the configuration options available for the `OpenAI` client, including base URL, and specific options for Azure OpenAI integration like `api_version` and `azure_endpoint`.

SOURCE: https://github.com/openai/openai-python/blob/main/README.md#_snippet_38

LANGUAGE: apidoc
CODE:
```
OpenAI:
  __init__(base_url: str = None, http_client: DefaultHttpxClient = None, ...)
    base_url: The base URL for the OpenAI API. Defaults to the official OpenAI API endpoint.
    http_client: An optional httpx.Client instance for custom configurations.

AzureOpenAI:
  __init__(api_version: str, azure_endpoint: str, azure_deployment: str = None, azure_ad_token: str = None, azure_ad_token_provider: callable = None, ...)
    api_version: The version of the Azure OpenAI API to use (e.g., "2023-07-01-preview").
    azure_endpoint: The Azure OpenAI endpoint URL.
    azure_deployment: The name of the Azure OpenAI deployment.
    azure_ad_token: A token for Azure Active Directory authentication.
    azure_ad_token_provider: A callable that provides an Azure AD token.

Common Options:
  - `base_url` (or `OPENAI_BASE_URL` env var)
  - `http_client` (for `OpenAI`)
  - `azure_endpoint` (or `AZURE_OPENAI_ENDPOINT` env var) (for `AzureOpenAI`)
  - `azure_deployment` (for `AzureOpenAI`)
  - `api_version` (or `OPENAI_API_VERSION` env var) (for `AzureOpenAI`)
  - `azure_ad_token` (or `AZURE_OPENAI_AD_TOKEN` env var) (for `AzureOpenAI`)
  - `azure_ad_token_provider` (for `AzureOpenAI`)
```

----------------------------------------

TITLE: OpenAI Beta Realtime Session Management
DESCRIPTION: API methods for creating and managing realtime conversation sessions.

SOURCE: https://github.com/openai/openai-python/blob/main/api.md#_snippet_29

LANGUAGE: APIDOC
CODE:
```
client.beta.realtime.sessions.create(**params) -> SessionCreateResponse
  - Creates a new realtime conversation session.
  - Parameters:
    - params: A dictionary of parameters for session creation (e.g., model, metadata).
  - Returns: A SessionCreateResponse object containing details of the created session.
```

----------------------------------------

TITLE: OpenAI Python Client Containers API Reference
DESCRIPTION: Detailed API reference for managing containers using the OpenAI Python client. This section outlines methods for creating new containers, retrieving existing ones by ID, listing all available containers, and deleting containers.

SOURCE: https://github.com/openai/openai-python/blob/main/api.md#_snippet_75

LANGUAGE: APIDOC
CODE:
```
POST /containers
client.containers.create(**params) -> ContainerCreateResponse
  - Creates a new container.
  - Parameters:
    - **params: Dictionary of parameters for container creation (e.g., name, configuration).
  - Returns: ContainerCreateResponse object upon successful creation.

GET /containers/{container_id}
client.containers.retrieve(container_id) -> ContainerRetrieveResponse
  - Retrieves a specific container by its unique identifier.
  - Parameters:
    - container_id: The ID of the container to retrieve.
  - Returns: ContainerRetrieveResponse object containing the container's details.

GET /containers
client.containers.list(**params) -> SyncCursorPage[ContainerListResponse]
  - Lists all containers, with support for pagination and filtering.
  - Parameters:
    - **params: Optional dictionary of parameters for listing containers (e.g., limit, after, before).
  - Returns: A paginated list (SyncCursorPage) of ContainerListResponse objects.

DELETE /containers/{container_id}
client.containers.delete(container_id) -> None
  - Deletes a specific container by its unique identifier.
  - Parameters:
    - container_id: The ID of the container to delete.
  - Returns: None upon successful deletion.
```

----------------------------------------

TITLE: Enabling Logging
DESCRIPTION: Shows how to enable logging for the OpenAI library by setting the OPENAI_LOG environment variable. Supports 'info' for general logs and 'debug' for verbose output.

SOURCE: https://github.com/openai/openai-python/blob/main/README.md#_snippet_28

LANGUAGE: shell
CODE:
```
export OPENAI_LOG=info
```

LANGUAGE: shell
CODE:
```
export OPENAI_LOG=debug
```

----------------------------------------

TITLE: Iterating Through Fine-Tuning Jobs (Sync)
DESCRIPTION: Demonstrates how to synchronously iterate through all fine-tuning jobs, fetching additional pages as needed. This is useful for processing large numbers of jobs without manual pagination.

SOURCE: https://github.com/openai/openai-python/blob/main/README.md#_snippet_15

LANGUAGE: python
CODE:
```
# Automatically fetches more pages as needed.
for job in client.fine_tuning.jobs.list(
    limit=20,
):
    # Do something with job here
    all_jobs.append(job)
print(all_jobs)
```

----------------------------------------

TITLE: Iterating Through Fine-Tuning Jobs (Async)
DESCRIPTION: Demonstrates how to asynchronously iterate through all fine-tuning jobs, fetching additional pages as needed. This is useful for processing large numbers of jobs without manual pagination.

SOURCE: https://github.com/openai/openai-python/blob/main/README.md#_snippet_14

LANGUAGE: python
CODE:
```
import asyncio
from openai import AsyncOpenAI

client = AsyncOpenAI()


async def main() -> None:
    all_jobs = []
    # Iterate through items across all pages, issuing requests as needed.
    async for job in client.fine_tuning.jobs.list(
        limit=20,
    ):
        all_jobs.append(job)
    print(all_jobs)


asyncio.run(main())
```

----------------------------------------

TITLE: Streaming Chat Completions with AsyncOpenAI
DESCRIPTION: Demonstrates how to use the `.chat.completions.stream()` method with `AsyncOpenAI` for asynchronous streaming of chat completions. It highlights the necessity of using a context manager for proper resource handling and iterating through events.

SOURCE: https://github.com/openai/openai-python/blob/main/helpers.md#_snippet_3

LANGUAGE: python
CODE:
```
from openai import AsyncOpenAI

client = AsyncOpenAI()

async with client.chat.completions.stream(
    model='gpt-4o-2024-08-06',
    messages=[...],
) as stream:
    async for event in stream:
        if event.type == 'content.delta':
            print(event.content, flush=True, end='')
```

----------------------------------------

TITLE: OpenAI API Reference - Assistants Streaming Events
DESCRIPTION: Provides detailed information on the types of events available for subscription within the OpenAI Assistant streaming API. Links to further documentation for specific event types and concepts.

SOURCE: https://github.com/openai/openai-python/blob/main/helpers.md#_snippet_13

LANGUAGE: APIDOC
CODE:
```
OpenAI Assistant Streaming Events:

- **General Events**:
  - `on_event(event: AssistantStreamEvent)`: Subscribe to all raw events.
  - `on_end()`: Triggered when the stream ends.
  - `on_timeout()`: Triggered if the request times out.
  - `on_exception(exception: Exception)`: Triggered if an exception occurs.

- **Run Step Events**:
  - `on_run_step_created(run_step: RunStep)`: Triggered when a RunStep is created.
  - `on_run_step_delta(delta: RunStepDelta, snapshot: RunStep)`: Triggered for RunStep updates.
  - `on_run_step_done(run_step: RunStep)`: Triggered when a RunStep completes.
  *See also: [Runs and RunSteps](https://platform.openai.com/docs/assistants/how-it-works/runs-and-run-steps)*

- **Message Events**:
  - `on_message_created(message: Message)`: Triggered when a Message is created.
  - `on_message_delta(delta: MessageDelta, snapshot: Message)`: Triggered for Message updates.
  - `on_message_done(message: Message)`: Triggered when a Message completes.
  *See also: [Message Object](https://platform.openai.com/docs/api-reference/messages/object)*

- **Text Content Events**:
  - `on_text_created(text: Text)`: Triggered when Text content is created.
  - `on_text_delta(delta: TextDelta, snapshot: Text)`: Triggered for Text content updates.
  - `on_text_done(text: Text)`: Triggered when Text content completes.

- **Image File Events**:
  - `on_image_file_done(image_file: ImageFile)`: Triggered when an ImageFile is available.

- **Tool Call Events**:
  - `on_tool_call_created(tool_call: ToolCall)`: Triggered when a ToolCall is created.
  - `on_tool_call_delta(delta: ToolCallDelta, snapshot: ToolCall)`: Triggered for ToolCall updates.
  - `on_tool_call_done(tool_call: ToolCall)`: Triggered when a ToolCall completes.
  *See also: [Tools](https://platform.openai.com/docs/assistants/tools)*

*For a comprehensive list of all possible raw events, refer to: [Events](https://platform.openai.com/docs/api-reference/assistants-streaming/events)*
```

----------------------------------------

TITLE: OpenAI Beta Realtime Transcription Session Management
DESCRIPTION: API methods for creating and managing realtime transcription sessions.

SOURCE: https://github.com/openai/openai-python/blob/main/api.md#_snippet_30

LANGUAGE: APIDOC
CODE:
```
client.beta.realtime.transcription_sessions.create(**params) -> TranscriptionSession
  - Creates a new realtime transcription session.
  - Parameters:
    - params: A dictionary of parameters for transcription session creation (e.g., model, language).
  - Returns: A TranscriptionSession object representing the created session.
```

----------------------------------------

TITLE: OpenAI API Reference - Assistants Convenience Methods
DESCRIPTION: Convenience methods available on the assistant streaming object to access contextual information during event handling or to retrieve final results after stream completion.

SOURCE: https://github.com/openai/openai-python/blob/main/helpers.md#_snippet_14

LANGUAGE: APIDOC
CODE:
```
Assistant Streaming Object Methods:

- **Context Access**:
  - `current_event() -> AssistantStreamEvent | None`: Returns the current event being processed.
  - `current_run() -> Run | None`: Returns the current Run object.
  - `current_message_snapshot() -> Message | None`: Returns a snapshot of the current Message.
  - `current_run_step_snapshot() -> RunStep | None`: Returns a snapshot of the current RunStep.
  *Note: Context may be `None` if not applicable.*

- **Final Result Retrieval**:
  - `get_final_run() -> Run`: Consumes the stream to completion and returns the final Run object.
  - `get_final_run_steps() -> List[RunStep]`: Consumes the stream to completion and returns a list of all RunStep objects.
  - `get_final_messages() -> List[Message]`: Consumes the stream to completion and returns a list of all Message objects.
```

----------------------------------------

TITLE: OpenAI Run Steps API
DESCRIPTION: Provides methods for retrieving and listing run steps associated with a specific run. These methods allow detailed inspection of the execution flow of a run.

SOURCE: https://github.com/openai/openai-python/blob/main/api.md#_snippet_36

LANGUAGE: APIDOC
CODE:
```
GET /threads/{thread_id}/runs/{run_id}/steps/{step_id}
  Description: Retrieves a specific run step by its ID.
  Parameters:
    step_id (str): The ID of the run step to retrieve.
    thread_id (str): The ID of the thread the run belongs to.
    run_id (str): The ID of the run the step belongs to.
    params (dict): Additional parameters for retrieval.
  Returns: RunStep object.

GET /threads/{thread_id}/runs/{run_id}/steps
  Description: Lists all steps for a given run.
  Parameters:
    run_id (str): The ID of the run to list steps for.
    thread_id (str): The ID of the thread the run belongs to.
    params (dict): Parameters for filtering and pagination (e.g., order, limit).
  Returns: SyncCursorPage of RunStep objects.
```

----------------------------------------

TITLE: OpenAI Python Client Batches API Methods
DESCRIPTION: Details the client methods for managing batch operations with the OpenAI API, covering creation, retrieval, listing, and cancellation of batches.

SOURCE: https://github.com/openai/openai-python/blob/main/api.md#_snippet_58

LANGUAGE: APIDOC
CODE:
```
client.batches.create(**params)
  - Description: Creates a new batch job.
  - HTTP Endpoint: POST /batches
  - Returns: Batch type object

client.batches.retrieve(batch_id)
  - Description: Retrieves a specific batch job by its ID.
  - HTTP Endpoint: GET /batches/{batch_id}
  - Returns: Batch type object

client.batches.list(**params)
  - Description: Lists all batch jobs.
  - HTTP Endpoint: GET /batches
  - Returns: SyncCursorPage[Batch] type object

client.batches.cancel(batch_id)
  - Description: Cancels a specific batch job.
  - HTTP Endpoint: POST /batches/{batch_id}/cancel
  - Returns: Batch type object
```

----------------------------------------

TITLE: OpenAI API Reference
DESCRIPTION: This section outlines the core functionalities and methods available through the OpenAI API client, including fine-tuning jobs, chat completions, file uploads, and webhook handling.

SOURCE: https://github.com/openai/openai-python/blob/main/README.md#_snippet_20

LANGUAGE: APIDOC
CODE:
```
OpenAIClient:
  __init__(api_key: str = None, organization: str = None, ...)
    Initializes the OpenAI client with optional API key and organization.

  fine_tuning.jobs:
    list(limit: int = 20, after: str = None, ...):
      Retrieves a list of fine-tuning jobs.
      Parameters:
        limit: Maximum number of jobs to return.
        after: A cursor for pagination, returning jobs after this job.
      Returns: A list of fine-tuning job objects.

    create(training_file: str, validation_file: str = None, ...):
      Creates a new fine-tuning job.
      Parameters:
        training_file: The ID of the training file.
        validation_file: The ID of the validation file.
      Returns: The created fine-tuning job object.

  chat.completions:
    create(model: str, messages: list, ...):
      Creates a completion for a chat conversation.
      Parameters:
        model: The ID of the model to use.
        messages: A list of messages comprising the conversation.
      Returns: A chat completion response object.

  files:
    create(file: bytes | PathLike | tuple, purpose: str, ...):
      Uploads a file to OpenAI.
      Parameters:
        file: The file to upload, as bytes, PathLike, or (filename, contents, media_type).
        purpose: The intended use of the file (e.g., "fine-tune").
      Returns: The file object.

  webhooks:
    unwrap(body: str, signature: str, ...):
      Parses and verifies a webhook payload.
      Parameters:
        body: The raw JSON string of the webhook request body.
        signature: The value of the 'OpenAI-Signature' header.
      Returns: The parsed event object.
      Raises: ValueError if the signature is invalid.
```

----------------------------------------

TITLE: Creating and Running a Thread (OpenAI Python)
DESCRIPTION: This method streamlines the process of creating a new thread and immediately initiating a run on it. It takes `params` for both thread creation and run configuration, returning a `Run` object representing the active execution.

SOURCE: https://github.com/openai/openai-python/blob/main/api.md#_snippet_95

LANGUAGE: Python
CODE:
```
client.beta.threads.create_and_run(**params)
```

----------------------------------------

TITLE: Generate Text with Responses API
DESCRIPTION: Generates text using the OpenAI Responses API with a specified model and instructions. It demonstrates setting the API key from an environment variable.

SOURCE: https://github.com/openai/openai-python/blob/main/README.md#_snippet_1

LANGUAGE: python
CODE:
```
import os
from openai import OpenAI

client = OpenAI(
    # This is the default and can be omitted
    api_key=os.environ.get("OPENAI_API_KEY"),
)

response = client.responses.create(
    model="gpt-4o",
    instructions="You are a coding assistant that talks like a pirate.",
    input="How do I check if a Python object is an instance of a class?",
)

print(response.output_text)
```

----------------------------------------

TITLE: Manual Pagination Control for Fine-Tuning Jobs
DESCRIPTION: Shows how to manually control pagination when fetching fine-tuning jobs. It demonstrates checking for the next page, retrieving it, and accessing pagination details like the cursor.

SOURCE: https://github.com/openai/openai-python/blob/main/README.md#_snippet_16

LANGUAGE: python
CODE:
```
# Remove `await` for non-async usage.
first_page = await client.fine_tuning.jobs.list(
    limit=20,
)
if first_page.has_next_page():
    print(f"will fetch next page using these details: {first_page.next_page_info()}")
    next_page = await first_page.get_next_page()
    print(f"number of items we just fetched: {len(next_page.data)}")

# Remove `await` for non-async usage.

first_page = await client.fine_tuning.jobs.list(
    limit=20,
)

print(f"next page cursor: {first_page.after}")  # => "next page cursor: ..."
for job in first_page.data:
    print(job.id)

# Remove `await` for non-async usage.
```

----------------------------------------

TITLE: OpenAI Python Client Uploads API Methods
DESCRIPTION: Outlines the client methods for managing file uploads to the OpenAI API, including operations for initiating, cancelling, and completing uploads.

SOURCE: https://github.com/openai/openai-python/blob/main/api.md#_snippet_60

LANGUAGE: APIDOC
CODE:
```
client.uploads.create(**params)
  - Description: Initiates a new file upload.
  - HTTP Endpoint: POST /uploads
  - Returns: Upload type object

client.uploads.cancel(upload_id)
  - Description: Cancels an ongoing file upload.
  - HTTP Endpoint: POST /uploads/{upload_id}/cancel
  - Returns: Upload type object

client.uploads.complete(upload_id, **params)
  - Description: Completes a multi-part file upload.
  - HTTP Endpoint: POST /uploads/{upload_id}/complete
  - Returns: Upload type object
```

----------------------------------------

TITLE: Add Audio Helpers
DESCRIPTION: Introduces new audio helper utilities to simplify common audio-related tasks and operations within the library.

SOURCE: https://github.com/openai/openai-python/blob/main/CHANGELOG.md#_snippet_27

LANGUAGE: APIDOC
CODE:
```
Feature: New audio helper utilities added.
```

----------------------------------------

TITLE: Using Nested Parameters for Chat Responses
DESCRIPTION: Illustrates how to use nested parameters, specifically for the `chat.responses.create` method. It shows how to structure the `input` and `response_format` parameters.

SOURCE: https://github.com/openai/openai-python/blob/main/README.md#_snippet_17

LANGUAGE: python
CODE:
```
from openai import OpenAI

client = OpenAI()

response = client.chat.responses.create(
    input=[
        {
            "role": "user",
            "content": "How much ?",
        }
    ],
    model="gpt-4o",
    response_format={"type": "json_object"},
)
```

----------------------------------------

TITLE: OpenAI Completions API
DESCRIPTION: Provides the method to create text completions using the OpenAI API. It takes parameters defining the prompt, model, and other generation settings, returning a Completion object.

SOURCE: https://github.com/openai/openai-python/blob/main/api.md#_snippet_2

LANGUAGE: APIDOC
CODE:
```
POST /completions
client.completions.create(**params) -> Completion

Description: Creates a completion for the provided prompt and parameters.
Parameters:
  params: A dictionary of parameters for the completion request. See openai.types.CompletionCreateParams for details.
Returns:
  Completion: An object containing the completion result.
```

----------------------------------------

TITLE: OpenAI Fine-Tuning Jobs API
DESCRIPTION: Manages fine-tuning jobs, including creation, retrieval, listing, cancellation, pausing, resuming, and listing events and checkpoints.

SOURCE: https://github.com/openai/openai-python/blob/main/api.md#_snippet_15

LANGUAGE: APIDOC
CODE:
```
OpenAI Fine-Tuning Jobs API:

POST /fine_tuning/jobs
  Create a new fine-tuning job.
  - Parameters: Accepts fine-tuning job creation parameters.
  - Returns: A FineTuningJob object.

GET /fine_tuning/jobs/{fine_tuning_job_id}
  Retrieve a specific fine-tuning job.
  - Parameters:
    - fine_tuning_job_id: The ID of the fine-tuning job.
  - Returns: A FineTuningJob object.

GET /fine_tuning/jobs
  List fine-tuning jobs.
  - Parameters: Accepts job list parameters.
  - Returns: A SyncCursorPage of FineTuningJob objects.

POST /fine_tuning/jobs/{fine_tuning_job_id}/cancel
  Cancel a fine-tuning job.
  - Parameters:
    - fine_tuning_job_id: The ID of the fine-tuning job to cancel.
  - Returns: A FineTuningJob object.

GET /fine_tuning/jobs/{fine_tuning_job_id}/events
  List events for a fine-tuning job.
  - Parameters:
    - fine_tuning_job_id: The ID of the fine-tuning job.
    - params: Accepts job event list parameters.
  - Returns: A SyncCursorPage of FineTuningJobEvent objects.

POST /fine_tuning/jobs/{fine_tuning_job_id}/pause
  Pause a fine-tuning job.
  - Parameters:
    - fine_tuning_job_id: The ID of the fine-tuning job to pause.
  - Returns: A FineTuningJob object.

POST /fine_tuning/jobs/{fine_tuning_job_id}/resume
  Resume a paused fine-tuning job.
  - Parameters:
    - fine_tuning_job_id: The ID of the fine-tuning job to resume.
  - Returns: A FineTuningJob object.

GET /fine_tuning/jobs/{fine_tuning_job_id}/checkpoints
  List checkpoints for a fine-tuning job.
  - Parameters:
    - fine_tuning_job_id: The ID of the fine-tuning job.
    - params: Accepts checkpoint list parameters.
  - Returns: A SyncCursorPage of FineTuningJobCheckpoint objects.
```

----------------------------------------

TITLE: Python Type Hinting for Vector Stores
DESCRIPTION: Provides Python type hints for various objects related to vector store files and file batches, enhancing code readability and maintainability.

SOURCE: https://github.com/openai/openai-python/blob/main/api.md#_snippet_25

LANGUAGE: python
CODE:
```
from openai.types.vector_stores import VectorStoreFile, VectorStoreFileDeleted, FileContentResponse
from openai.types.vector_stores import VectorStoreFileBatch
```

----------------------------------------

TITLE: OpenAI Python Run Step Types
DESCRIPTION: Imports for various types related to OpenAI run steps, including different tool call types, step details, and overall run step objects.

SOURCE: https://github.com/openai/openai-python/blob/main/api.md#_snippet_38

LANGUAGE: python
CODE:
```
from openai.types.beta.threads.runs import (
    CodeInterpreterLogs,
    CodeInterpreterOutputImage,
    CodeInterpreterToolCall,
    CodeInterpreterToolCallDelta,
    FileSearchToolCall,
    FileSearchToolCallDelta,
    FunctionToolCall,
    FunctionToolCallDelta,
    MessageCreationStepDetails,
    RunStep,
    RunStepDelta,
    RunStepDeltaEvent,
    RunStepDeltaMessageDelta,
    RunStepInclude,
    ToolCall,
    ToolCallDelta,
    ToolCallDeltaObject,
    ToolCallsStepDetails,
)
```

----------------------------------------

TITLE: OpenAI Python Client Container Files API Reference
DESCRIPTION: Detailed API reference for managing files within specific containers using the OpenAI Python client. This section covers methods for creating, retrieving, listing, and deleting files associated with a given container.

SOURCE: https://github.com/openai/openai-python/blob/main/api.md#_snippet_76

LANGUAGE: APIDOC
CODE:
```
POST /containers/{container_id}/files
client.containers.files.create(container_id, **params) -> FileCreateResponse
  - Creates a new file within a specified container.
  - Parameters:
    - container_id: The ID of the container where the file will be created.
    - **params: Dictionary of parameters for file creation (e.g., file content, name).
  - Returns: FileCreateResponse object upon successful creation.

GET /containers/{container_id}/files/{file_id}
client.containers.files.retrieve(file_id, *, container_id) -> FileRetrieveResponse
  - Retrieves a specific file by its ID from a specified container.
  - Parameters:
    - file_id: The ID of the file to retrieve.
    - container_id: The ID of the container the file belongs to.
  - Returns: FileRetrieveResponse object containing the file's details.

GET /containers/{container_id}/files
client.containers.files.list(container_id, **params) -> SyncCursorPage[FileListResponse]
  - Lists all files within a specified container, with support for pagination and filtering.
  - Parameters:
    - container_id: The ID of the container whose files are to be listed.
    - **params: Optional dictionary of parameters for listing files.
  - Returns: A paginated list (SyncCursorPage) of FileListResponse objects.

DELETE /containers/{container_id}/files/{file_id}
client.containers.files.delete(file_id, *, container_id) -> None
  - Deletes a specific file by its ID from a specified container.
  - Parameters:
    - file_id: The ID of the file to delete.
    - container_id: The ID of the container the file belongs to.
  - Returns: None upon successful deletion.
```

----------------------------------------

TITLE: Assistant Streaming API - Iterating Over Events
DESCRIPTION: Shows how to iterate through all streamed events from the Assistant API. This allows for granular processing of each event as it arrives, such as printing text delta content.

SOURCE: https://github.com/openai/openai-python/blob/main/helpers.md#_snippet_7

LANGUAGE: python
CODE:
```
with client.beta.threads.runs.stream(
  thread_id=thread.id,
  assistant_id=assistant.id
) as stream:
    for event in stream:
        # Print the text from text delta events
        if event.event == "thread.message.delta" and event.data.delta.content:
            print(event.data.delta.content[0].text)
```

----------------------------------------

TITLE: OpenAI Python Run Types
DESCRIPTION: Imports for various types related to OpenAI runs and their components, including status, tool calls, and step details.

SOURCE: https://github.com/openai/openai-python/blob/main/api.md#_snippet_37

LANGUAGE: python
CODE:
```
from openai.types.beta.threads import RequiredActionFunctionToolCall, Run, RunStatus
```

----------------------------------------

TITLE: OpenAI Polling Helpers
DESCRIPTION: SDK helper functions for polling asynchronous API actions until they reach a terminal state. These methods simplify managing operations like creating runs or uploading files.

SOURCE: https://github.com/openai/openai-python/blob/main/helpers.md#_snippet_12

LANGUAGE: python
CODE:
```
client.beta.threads.create_and_run_poll(...)
client.beta.threads.runs.create_and_poll(...)
client.beta.threads.runs.submit_tool_outputs_and_poll(...)
client.beta.vector_stores.files.upload_and_poll(...)
client.beta.vector_stores.files.create_and_poll(...)
client.beta.vector_stores.file_batches.create_and_poll(...)
client.beta.vector_stores.file_batches.upload_and_poll(...)
```

----------------------------------------

TITLE: Using TypedDicts and Pydantic Models
DESCRIPTION: Explains the use of TypedDicts for request parameters and Pydantic models for responses in the OpenAI Python library. These provide type safety and helper methods.

SOURCE: https://github.com/openai/openai-python/blob/main/README.md#_snippet_13

LANGUAGE: python
CODE:
```
from openai import OpenAI

client = OpenAI()

all_jobs = []

```

----------------------------------------

TITLE: Streaming Responses with Synchronous Client
DESCRIPTION: Shows how to handle streaming responses from the OpenAI API using the synchronous client. It iterates over events as they are received.

SOURCE: https://github.com/openai/openai-python/blob/main/README.md#_snippet_9

LANGUAGE: python
CODE:
```
from openai import OpenAI

client = OpenAI()

stream = client.responses.create(
    model="gpt-4o",
    input="Write a one-sentence bedtime story about a unicorn.",
    stream=True,
)

for event in stream:
    print(event)
```

----------------------------------------

TITLE: Making Undocumented POST Requests
DESCRIPTION: Shows how to make requests to undocumented API endpoints using `client.post`. It demonstrates specifying the response type and providing a request body.

SOURCE: https://github.com/openai/openai-python/blob/main/README.md#_snippet_32

LANGUAGE: python
CODE:
```
import httpx

response = client.post(
    "/foo",
    cast_to=httpx.Response,
    body={"my_param": True},
)

print(response.headers.get("x-foo"))
```

----------------------------------------

TITLE: Vector Store File Batches API
DESCRIPTION: Manages batches of files within OpenAI vector stores. Includes methods for creating, retrieving, canceling batches, and listing files within a batch. Supports asynchronous operations and polling.

SOURCE: https://github.com/openai/openai-python/blob/main/api.md#_snippet_24

LANGUAGE: APIDOC
CODE:
```
VectorStoreFileBatches:
  create(vector_store_id: str, **params) -> VectorStoreFileBatch
    POST /vector_stores/{vector_store_id}/file_batches
    Creates a batch of files for a vector store.
    Parameters:
      vector_store_id: The ID of the vector store.
      **params: Parameters for creating the file batch (e.g., file_ids).
    Returns: The created VectorStoreFileBatch object.

  retrieve(batch_id: str, *, vector_store_id: str) -> VectorStoreFileBatch
    GET /vector_stores/{vector_store_id}/file_batches/{batch_id}
    Retrieves a specific file batch from a vector store.
    Parameters:
      batch_id: The ID of the file batch to retrieve.
      vector_store_id: The ID of the vector store.
    Returns: The VectorStoreFileBatch object.

  cancel(batch_id: str, *, vector_store_id: str) -> VectorStoreFileBatch
    POST /vector_stores/{vector_store_id}/file_batches/{batch_id}/cancel
    Cancels a file batch in a vector store.
    Parameters:
      batch_id: The ID of the file batch to cancel.
      vector_store_id: The ID of the vector store.
    Returns: The updated VectorStoreFileBatch object.

  list_files(batch_id: str, *, vector_store_id: str, **params) -> SyncCursorPage[VectorStoreFile]
    GET /vector_stores/{vector_store_id}/file_batches/{batch_id}/files
    Lists all files within a specific file batch.
    Parameters:
      batch_id: The ID of the file batch.
      vector_store_id: The ID of the vector store.
      **params: Additional parameters for listing files (e.g., limit, order).
    Returns: A SyncCursorPage of VectorStoreFile objects.

  create_and_poll(*args) -> VectorStoreFileBatch
    Handles creation and polling for vector store file batches.

  poll(*args) -> VectorStoreFileBatch
    Polls the status of vector store file batch operations.

  upload_and_poll(*args) -> VectorStoreFileBatch
    Handles uploading and polling for vector store file batches.
```