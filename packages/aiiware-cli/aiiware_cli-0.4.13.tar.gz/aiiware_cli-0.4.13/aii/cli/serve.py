"""CLI command to start AII API server."""

import asyncio
import sys
from typing import List

from aii.api.server import APIServer, generate_api_key, server as global_server_var
from aii.core.engine import AIIEngine
from aii.config.manager import ConfigManager
import aii.api.server as server_module


async def start_api_server(host: str, port: int, api_keys: List[str], verbose: bool = False):
    """
    Start AII API server.

    Args:
        host: Server host (0.0.0.0 for all interfaces)
        port: Server port (8080 default)
        api_keys: List of API keys (auto-generates if empty)
        verbose: Enable verbose logging
    """

    print("🚀 Initializing AII API server...")

    # Initialize config and engine
    from pathlib import Path
    from aii.config.output_config import OutputConfig
    from aii.functions import register_all_functions
    from aii.functions.system.system_functions import HelpFunction, ClarificationFunction

    config_manager = ConfigManager()
    config = config_manager.get_all_config()
    storage_path = Path.home() / ".aii"

    # Create output config
    output_config = OutputConfig()

    # Create engine
    engine = AIIEngine(
        config=config,
        storage_path=storage_path,
        output_config=output_config,
        config_manager=config_manager
    )

    # Register all built-in functions
    register_all_functions(engine.function_registry)
    engine.register_function(HelpFunction())
    engine.register_function(ClarificationFunction())

    # Configure API keys
    if not api_keys:
        # Generate default key
        default_key = generate_api_key()
        print(f"\n🔑 Generated API key: {default_key}")
        print(f"   Use this key in AII-API-Key header")
        print(f"   Example: curl -H 'AII-API-Key: {default_key}' http://{host if host != '0.0.0.0' else 'localhost'}:{port}/api/status\n")
        api_keys = [default_key]
    else:
        print(f"🔑 Using {len(api_keys)} configured API key(s)\n")

    config_manager.set("api.keys", api_keys)

    # Create server
    api_server = APIServer(engine, config_manager)

    # Set global server instance
    server_module.server = api_server

    # Print startup info
    print(f"🚀 AII API server starting...")
    print(f"   Host: {host}")
    print(f"   Port: {port}")
    print(f"   OpenAPI docs: http://{host if host != '0.0.0.0' else 'localhost'}:{port}/docs")
    print(f"   Status: http://{host if host != '0.0.0.0' else 'localhost'}:{port}/api/status")
    print(f"\n✅ Server ready - Press Ctrl+C to stop\n")

    try:
        # Start server
        await api_server.start_server(host, port)
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down server...")
        await api_server.shutdown()
        await engine.shutdown()
        print("✅ Server stopped")
    except Exception as e:
        print(f"\n❌ Server error: {e}")
        await api_server.shutdown()
        await engine.shutdown()
        sys.exit(1)


def serve_command_sync(host: str, port: int, api_key: tuple, verbose: bool):
    """Synchronous wrapper for async serve command."""
    try:
        asyncio.run(start_api_server(host, port, list(api_key), verbose))
    except KeyboardInterrupt:
        # Already handled in async function
        pass
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        sys.exit(1)
