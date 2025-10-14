"""
MCP (Model Context Protocol) server for exposing a vectorized codebase.
Final production version — compatible with PyPI `mcp-server` (FastMCP).
"""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Any

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

try:
    # ✅ Works with the installed mcp-server package
    from mcp_server.server import FastMCP, Context

    MCP_AVAILABLE = True
except ImportError as e:
    MCP_AVAILABLE = False
    logger.warning(f"MCP not available ({e}); running fallback HTTP server.")


# =============================================================================
#                               MCP Server
# =============================================================================
class MCPServer:
    """MCP server exposing project-vectorizer tools and resources."""

    def __init__(self, project_manager, host: str = "localhost", port: int = 8000):
        self.project_manager = project_manager
        self.host = host
        self.port = port

        if MCP_AVAILABLE:
            self.server = FastMCP("project-vectorizer", "0.1.0")
            self._register_tools()
        else:
            self.server = None

    # ---------------------------------------------------------------------
    # Tool registration (FastMCP decorator-based API)
    # ---------------------------------------------------------------------
    def _register_tools(self):
        """Register MCP tools for Gemini and other MCP clients."""

        @self.server.tool()
        async def search_code(context: Context, query: str, limit: int = 10, threshold: float = 0.5) -> str:
            """Search through the vectorized codebase."""
            try:
                results = await self.project_manager.search(query, limit=limit, threshold=threshold)
                payload = {
                    "query": query,
                    "total_results": len(results),
                    "results": results,
                }
                return json.dumps(payload, indent=2, default=str)
            except Exception as e:
                logger.exception("Error in search_code tool")
                return f"Error: {e}"

        @self.server.tool()
        async def get_file_content(context: Context, file_path: str) -> str:
            """Retrieve file content."""
            try:
                content = await self.project_manager.get_file_content(file_path)
                if content is None:
                    raise FileNotFoundError(f"File not found: {file_path}")
                return content
            except Exception as e:
                logger.exception("Error in get_file_content tool")
                return f"Error: {e}"

        @self.server.tool()
        async def list_files(context: Context, file_type: str | None = None) -> str:
            """List all files in the project."""
            try:
                files = await self.project_manager.list_files(file_type_filter=file_type)
                return json.dumps({"files": files, "total_files": len(files)}, indent=2)
            except Exception as e:
                logger.exception("Error in list_files tool")
                return f"Error: {e}"

        @self.server.tool()
        async def get_project_stats(context: Context) -> str:
            """Get project statistics."""
            try:
                stats = await self.project_manager.get_status()
                return json.dumps(stats, indent=2, default=str)
            except Exception as e:
                logger.exception("Error in get_project_stats tool")
                return f"Error: {e}"

    # ---------------------------------------------------------------------
    # Start MCP server (synchronous wrapper)
    # ---------------------------------------------------------------------
    def start(self):
        """Start MCP server using FastMCP (non-async wrapper)."""
        if not MCP_AVAILABLE:
            logger.warning("MCP not installed; starting fallback HTTP server.")
            asyncio.run(SimpleHTTPFallback(self.project_manager, self.host, self.port).start())
            return

        try:
            logger.info("Starting MCP FastMCP server...")
            # ✅ FastMCP manages its own asyncio loop internally
            self.server.run()
        except Exception as e:
            logger.error(f"Failed to start MCP FastMCP server: {e}")
            asyncio.run(SimpleHTTPFallback(self.project_manager, self.host, self.port).start())


# =============================================================================
#                         Fallback HTTP Server (optional)
# =============================================================================
class SimpleHTTPFallback:
    """Fallback aiohttp server if MCP is unavailable."""

    def __init__(self, project_manager, host="localhost", port=8000):
        self.project_manager = project_manager
        self.host = host
        self.port = port

    async def start(self):
        """Start a lightweight HTTP fallback server."""
        try:
            from aiohttp import web

            app = web.Application()
            app.router.add_get("/health", self._health)
            app.router.add_get("/search", self._search)
            app.router.add_get("/file/{path:.*}", self._file)
            app.router.add_get("/files", self._files)
            app.router.add_get("/stats", self._stats)

            runner = web.AppRunner(app)
            await runner.setup()
            site = web.TCPSite(runner, self.host, self.port)
            await site.start()
            logger.info(f"Fallback HTTP server running at http://{self.host}:{self.port}")

            while True:
                await asyncio.sleep(3600)

        except ImportError:
            logger.error("aiohttp not installed; cannot run fallback HTTP server.")
        except Exception as e:
            logger.exception(f"Fallback server failed: {e}")

    async def _health(self, request):
        from aiohttp import web
        return web.json_response({"status": "healthy"})

    async def _search(self, request):
        from aiohttp import web
        try:
            query = request.query.get("q", "")
            if not query:
                return web.json_response({"error": "Missing 'q' parameter"}, status=400)
            limit = int(request.query.get("limit", 10))
            threshold = float(request.query.get("threshold", 0.5))
            results = await self.project_manager.search(query, limit=limit, threshold=threshold)
            return web.json_response({"query": query, "results": results, "total": len(results)})
        except Exception as e:
            return web.json_response({"error": str(e)}, status=500)

    async def _file(self, request):
        from aiohttp import web
        file_path = request.match_info["path"]
        try:
            content = await self.project_manager.get_file_content(file_path)
            if content is None:
                return web.json_response({"error": "File not found"}, status=404)
            return web.Response(text=content, content_type="text/plain")
        except Exception as e:
            return web.json_response({"error": str(e)}, status=500)

    async def _files(self, request):
        from aiohttp import web
        try:
            file_type = request.query.get("type")
            files = await self.project_manager.list_files(file_type_filter=file_type)
            return web.json_response({"files": files, "total": len(files)})
        except Exception as e:
            return web.json_response({"error": str(e)}, status=500)

    async def _stats(self, request):
        from aiohttp import web
        try:
            stats = await self.project_manager.get_status()
            return web.json_response(stats, dumps=lambda d: json.dumps(d, default=str))
        except Exception as e:
            return web.json_response({"error": str(e)}, status=500)
