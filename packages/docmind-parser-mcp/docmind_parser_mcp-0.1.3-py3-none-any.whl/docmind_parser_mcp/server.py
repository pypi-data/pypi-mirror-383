"""
DocMind Parser MCP Server (Custom FastMCP Version)
"""
import os
from typing import Dict
from mcp.server import Server as LowLevelServer
from mcp.server.fastmcp import FastMCP
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.routing import Mount, Route

from ._uri_utils import file_uri_to_path
from .config import config
from doc_json_sdk.handler.document_handler import DocumentParserWithCallbackHandler
from doc_json_sdk.loader.document_model_loader import DocumentModelLoader


# 创建 FastMCP 实例（它是对 LowLevelServer 的封装）
mcp = FastMCP("docmind-parser")


# 使用 mcp 实例的 .tool() 方法注册工具（✅ 正确方式）
@mcp.tool()
def convert_to_markdown(uri: str) -> str:
    """
    Convert a document (file:/http:/https:) to markdown.
    """
    file_path = None
    file_url = None

    if uri.startswith("file:"):
        netloc, path = file_uri_to_path(uri)
        if netloc and netloc != "localhost":
            raise ValueError(f"Unsupported file URI host: {netloc}. Only localhost or empty allowed.")
        file_path = path
    elif os.path.exists(uri):
        file_path = uri
    elif uri.startswith("http://") or uri.startswith("https://"):
        file_url = uri
    else:
        raise ValueError(f"Unsupported URI scheme: {uri.split(':')[0]}. Supported: file:, http:, https:")

    md_result = ""

    def callback(arg: Dict):
        nonlocal md_result
        if "markdownContent" in arg:
            md_result += arg["markdownContent"]

    try:
        loader = DocumentModelLoader(
            handler=DocumentParserWithCallbackHandler(callback=callback)
        )
        structure_type = config.get("parse", {}).get("structure_type", "layout")
        formula_enhancement = config.get("parse", {}).get("formula_enhancement", False)
        llm_enhancement = config.get("parse", {}).get("llm_enhancement", False)

        loader.load(
            file_path=file_path,
            file_url=file_url,
            reveal_markdown=True,
            structure_type=structure_type,
            llm_enhancement=llm_enhancement,
            formula_enhancement=formula_enhancement
        )
    except Exception as e:
        raise RuntimeError(f"Failed to parse document: {str(e)}") from e

    if not md_result.strip():
        raise ValueError("Parsed markdown is empty. The document may be unsupported or corrupted.")

    return md_result


# ========== Transport: SSE ==========
def create_sse_app(mcp_server: LowLevelServer) -> Starlette:
    sse = SseServerTransport("/messages/")

    async def handle_sse(request: Request):
        async with sse.connect_sse(
            request.scope,
            request.receive,
            request._send,
        ) as (read_stream, write_stream):
            await mcp_server.run(
                read_stream,
                write_stream,
                mcp_server.create_initialization_options(),
            )

    return Starlette(
        debug=True,
        routes=[
            Route("/sse", endpoint=handle_sse),
            Mount("/messages/", app=sse.handle_post_message),
        ],
    )


# ========== Start Server ==========
def start_main():
    protocol = config.get("server", {}).get("protocol_mode") or "stdio"
    mcp_server = mcp._mcp_server  # 获取底层 Server 实例

    if protocol == "sse":
        app = create_sse_app(mcp_server)
        host = config.get("server", {}).get("bind_host") or "127.0.0.1"
        port = config.get("server", {}).get("listen_port") or 3001
        print(f"🚀 Starting SSE server at http://{host}:{port}/sse")
        import uvicorn
        uvicorn.run(app, host=host, port=port)
    else:
        print("🔁 Starting MCP server over STDIO...")
        mcp.run(transport="stdio")


if __name__ == "__main__":
    start_main()