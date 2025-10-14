from mcp.server import Server
import asyncio


def run_stdio(server: Server):
    """Run MCP server over stdin/stdout."""
    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        server.run(
            input_stream=server._create_stdin_input_stream(),
            output_stream=server._create_stdout_output_stream(),
            initialization_options=server.create_initialization_options(),
        )
    )