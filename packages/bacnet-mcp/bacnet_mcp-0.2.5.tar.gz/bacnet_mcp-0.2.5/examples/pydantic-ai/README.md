## PydanticAI MCP Example

This example demonstrates how to use the [PydanticAI Agent Framework](https://ai.pydantic.dev) to connect to the [BACnet MCP server](https://github.com/ezhuk/bacnet-mcp) using the `Streamable HTTP` transport.

## Getting Started

Run the following command to install `uv` or check out the [installation guide](https://docs.astral.sh/uv/getting-started/installation/) for more details and alternative installation methods.

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Clone the repository, then use `uv` to install project dependencies and create a virtual environment.

```bash
git clone https://github.com/ezhuk/bacnet-mcp.git
cd bacnet-mcp/examples/pydantic-ai
uv sync
```

Start the BACnet MCP server in a separate terminal window and leave it running.

```bash
uv run bacnet-mcp
```

Make sure the `OPENAI_API_KEY` environment variable is set and run the example.

```bash
uv run main.py
```

You should see the output similar to the following.

```text
Running: Read the presentValue property of analogInput,1.
The value of the presentValue property is 123.
Running: Write the value 42 to analogValue instance 1.
The value 42 was successfully written to AnalogValue instance 1.
```

Modify the prompts in the `main` function depending on the target BACnet device.
