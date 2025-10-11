"""Entry point for directory browser MCP server"""

import asyncio
from .server import main as async_main


def main():
    """同步入口点函数"""
    asyncio.run(async_main())


if __name__ == "__main__":
    main()