# %% [markdown]

# %%
from __future__ import annotations

import asyncio
import threading
import time
from collections.abc import Awaitable, Callable
from datetime import datetime, timezone
from typing import Any

import anyio
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings
from mcp.types import TextContent, TextResourceContents
from pydantic import AnyUrl


def _text_from_content(content: list[Any]) -> str:
    """Extract plain text from MCP tool/resource content blocks."""
    parts: list[str] = []
    for block in content:
        if isinstance(block, TextContent):
            parts.append(block.text)
        elif getattr(block, "type", None) == "text":
            parts.append(block.text)
    return "\n".join(parts)


def _run_async(
    coro_func: Callable[..., Awaitable[Any]],
    *args: Any,
    **kwargs: Any,
) -> None:
    """Run async demo in plain script or Jupyter without nested-loop errors."""
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        anyio.run(coro_func, *args, **kwargs)
        return

    # Jupyter/IPython already runs asyncio; anyio.run() would fail here.
    errors: list[BaseException] = []

    def _worker() -> None:
        try:
            anyio.run(coro_func, *args, **kwargs)
        except BaseException as exc:
            errors.append(exc)

    thread = threading.Thread(
        target=_worker,
        name=f"mcp-demo-{getattr(coro_func, '__name__', 'async')}",
    )
    thread.start()
    thread.join()
    if errors:
        raise errors[0]


# %% [markdown]
# ## 1. 创建 MCP 示例
#
# 使用 FastMCP 定义工具与资源，供 streamable HTTP 传输使用。

# %%
mcp = FastMCP(
    "MCP Demo",
    instructions="A minimal demo MCP server with a few example tools and resources.",
    stateless_http=True,
    transport_security=TransportSecuritySettings(
        enable_dns_rebinding_protection=False,
    ),
    log_level="WARNING",
)


@mcp.tool()
async def add(a: float, b: float) -> float:
    """Add two numbers."""
    return a + b


@mcp.tool()
async def greet(name: str) -> str:
    """Return a greeting for the given name."""
    return f"Hello, {name}!"


@mcp.tool()
async def echo(message: str, repeat: int = 1) -> str:
    """Echo a message, optionally repeated."""
    if repeat < 1:
        raise ValueError("repeat must be >= 1")
    return " ".join([message] * repeat)


@mcp.resource("demo://server-info")
def server_info() -> str:
    """Static resource with basic server metadata."""
    now = datetime.now(timezone.utc).isoformat()
    return f"MCP Demo server (utc={now})"


# %% [markdown]
# ## 2. 启动 HTTP MCP 服务并调用示例
#
# 后台线程启动 streamable HTTP 服务，客户端连接后列出工具、调用工具并读取资源。


# %%
async def _mcp_http_server(host: str, port: int) -> None:
    """Run uvicorn with FastMCP streamable HTTP app."""
    import uvicorn

    app = mcp.streamable_http_app()
    config = uvicorn.Config(app, host=host, port=port, log_level="warning")
    server = uvicorn.Server(config)
    await server.serve()


def start_server(host: str = "127.0.0.1", port: int = 8001) -> str:
    """Start streamable HTTP MCP server in a daemon background thread."""
    thread = threading.Thread(
        target=lambda: asyncio.run(_mcp_http_server(host, port)),
        name="mcp-http-server",
        daemon=True,
    )
    thread.start()
    return f"http://{host}:{port}/mcp"


def wait_for_mcp_http_server(url: str, timeout: float = 5.0) -> None:
    """Poll until the HTTP MCP endpoint accepts connections."""
    import httpx

    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            with httpx.Client(timeout=1.0) as client:
                # Any HTTP response means the listener is up.
                client.post(
                    url,
                    json={
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "initialize",
                        "params": {},
                    },
                )
            return
        except (httpx.HTTPError, OSError):
            time.sleep(0.1)
    raise TimeoutError(f"MCP HTTP server not ready at {url} within {timeout}s")


async def run_mcp_http_demo() -> None:
    """Start HTTP server (if needed), connect, and run demo MCP calls."""

    url = start_server()

    wait_for_mcp_http_server(url)

    print(f"HTTP MCP server ready at {url}")

    async with streamable_http_client(url) as (rs, ws, get_session_id):
        async with ClientSession(rs, ws) as session:
            init = await session.initialize()
            print(f"connected: {init.serverInfo.name} (session={get_session_id()})")

            tools = await session.list_tools()
            print("tools:", [tool.name for tool in tools.tools])

            add_result = await session.call_tool("add", {"a": 3, "b": 5})
            print("add(3, 5) =>", _text_from_content(add_result.content))

            greet_result = await session.call_tool("greet", {"name": "MCP"})
            print("greet('MCP') =>", _text_from_content(greet_result.content))

            resource = await session.read_resource(AnyUrl("demo://server-info"))
            resource_text = next(
                (
                    block.text
                    for block in resource.contents
                    if isinstance(block, (TextContent, TextResourceContents))
                ),
                str(resource),
            )
            print("resource demo://server-info =>", resource_text)


_run_async(run_mcp_http_demo)

# %%
