"""MCP Server for Directory Browser"""

import asyncio
from pathlib import Path
from typing import Any

from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest,
    ListToolsRequest,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
)

from .directory_ops import DirectoryOperations
from .security import SecurityManager


class DirectoryBrowserServer:
    """目录浏览MCP服务器"""

    def __init__(self, config_path: str = None):
        self.server = Server("directory-browser")
        self.directory_ops = DirectoryOperations()
        self.security_manager = SecurityManager(config_path)

        # 注册工具
        self._register_tools()
        # 注册Roots协议处理器（若SDK支持）
        self._register_roots()

    def _register_tools(self):
        """注册MCP工具"""

        @self.server.list_tools()
        async def handle_list_tools() -> list[Tool]:
            """列出可用的工具"""
            return [
                Tool(
                    name="list_directory",
                    description="列出目录中的文件和子目录",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "要列出的目录路径"
                            },
                            "show_hidden": {
                                "type": "boolean",
                                "description": "是否显示隐藏文件（以.开头的文件）",
                                "default": False
                            }
                        },
                        "required": ["path"]
                    }
                ),
                Tool(
                    name="get_file_info",
                    description="获取文件或目录的详细信息",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "文件或目录的路径"
                            }
                        },
                        "required": ["path"]
                    }
                ),
                Tool(
                    name="check_path_access",
                    description="检查路径的访问权限",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "要检查的路径"
                            }
                        },
                        "required": ["path"]
                    }
                ),
                Tool(
                    name="open_directory",
                    description="在系统文件管理器中打开目录",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "要打开的目录路径"
                            }
                        },
                        "required": ["path"]
                    }
                )
            ]

        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: dict) -> list[TextContent]:
            """处理工具调用"""
            try:
                if name == "list_directory":
                    return await self._handle_list_directory(arguments)
                elif name == "get_file_info":
                    return await self._handle_get_file_info(arguments)
                elif name == "check_path_access":
                    return await self._handle_check_path_access(arguments)
                elif name == "open_directory":
                    return await self._handle_open_directory(arguments)
                else:
                    return [TextContent(
                        type="text",
                        text=f"未知工具: {name}"
                    )]

            except Exception as e:
                return [TextContent(
                    type="text",
                    text=f"工具执行出错: {str(e)}"
                )]

    async def _handle_list_directory(self, arguments: dict) -> list[TextContent]:
        """处理列出目录请求"""
        path = arguments.get("path")
        show_hidden = arguments.get("show_hidden", False)

        if not path:
            return [TextContent(
                type="text",
                text="错误: 未提供路径参数"
            )]

        # 安全检查
        validation = self.security_manager.validate_request(path, "list")
        if not validation["valid"]:
            return [TextContent(
                type="text",
                text=f"访问被拒绝: {validation['error']}"
            )]

        # 执行目录列表操作
        result = self.directory_ops.list_directory(
            validation["path"],
            show_hidden
        )

        if "error" in result:
            return [TextContent(
                type="text",
                text=f"列出目录失败: {result['error']}"
            )]

        # 格式化输出
        output = self._format_directory_listing(result)

        return [TextContent(
            type="text",
            text=output
        )]

    async def _handle_get_file_info(self, arguments: dict) -> list[TextContent]:
        """处理获取文件信息请求"""
        path = arguments.get("path")

        if not path:
            return [TextContent(
                type="text",
                text="错误: 未提供路径参数"
            )]

        # 安全检查
        validation = self.security_manager.validate_request(path, "info")
        if not validation["valid"]:
            return [TextContent(
                type="text",
                text=f"访问被拒绝: {validation['error']}"
            )]

        # 获取文件信息
        result = self.directory_ops.get_file_info(validation["path"])

        if "error" in result:
            return [TextContent(
                type="text",
                text=f"获取文件信息失败: {result['error']}"
            )]

        # 格式化输出
        output = self._format_file_info(result)

        return [TextContent(
            type="text",
            text=output
        )]

    async def _handle_check_path_access(self, arguments: dict) -> list[TextContent]:
        """处理检查路径访问权限请求"""
        path = arguments.get("path")

        if not path:
            return [TextContent(
                type="text",
                text="错误: 未提供路径参数"
            )]

        # 执行访问检查
        result = self.directory_ops.check_path_access(path)
        security_check = self.security_manager.is_path_allowed(path)

        # 合并结果
        combined_result = {
            **result,
            "security_allowed": security_check["allowed"],
            "security_reason": security_check.get("reason", "")
        }

        if "error" in result:
            return [TextContent(
                type="text",
                text=f"检查访问权限失败: {result['error']}"
            )]

        # 格式化输出
        output = self._format_access_info(combined_result)

        return [TextContent(
            type="text",
            text=output
        )]

    async def _handle_open_directory(self, arguments: dict) -> list[TextContent]:
        """处理打开目录请求"""
        path = arguments.get("path")

        if not path:
            return [TextContent(
                type="text",
                text="错误: 未提供路径参数"
            )]

        # 安全检查
        validation = self.security_manager.validate_request(path, "open")
        if not validation["valid"]:
            return [TextContent(
                type="text",
                text=f"访问被拒绝: {validation['error']}"
            )]

        # 执行打开目录操作
        result = self.directory_ops.open_directory(validation["path"])

        if "error" in result:
            return [TextContent(
                type="text",
                text=f"打开目录失败: {result['error']}"
            )]

        return [TextContent(
            type="text",
            text=result["message"]
        )]

    def _register_roots(self) -> None:
        """注册Roots协议相关处理器"""
        if not hasattr(self.server, "list_roots"):
            return

        @self.server.list_roots()  # type: ignore[attr-defined]
        async def handle_list_roots() -> dict[str, Any]:
            """返回允许访问的根目录列表"""
            roots = self._build_root_entries()
            return {"roots": roots}

    def _build_root_entries(self) -> list[dict[str, str]]:
        """根据安全配置构建Root对象列表"""
        roots: list[dict[str, str]] = []
        seen_uris: set[str] = set()

        for directory in self.security_manager.get_allowed_directories():
            path = Path(directory).expanduser()
            try:
                resolved_path = path.resolve()
            except Exception:
                # 跳过无法解析的路径
                continue

            try:
                uri = resolved_path.as_uri()
            except ValueError:
                # 跳过无法转换为file URI的路径
                continue

            if uri in seen_uris:
                continue

            seen_uris.add(uri)
            name = resolved_path.name or str(resolved_path)
            roots.append({"uri": uri, "name": name})

        if not roots:
            # 若没有可用路径，使用当前工作目录作为兜底
            fallback_path = Path.cwd().resolve()
            try:
                fallback_uri = fallback_path.as_uri()
            except ValueError:
                fallback_uri = None

            if fallback_uri and fallback_uri not in seen_uris:
                fallback_name = fallback_path.name or str(fallback_path)
                roots.append({"uri": fallback_uri, "name": fallback_name})

        return roots

    def _format_directory_listing(self, result: dict) -> str:
        """格式化目录列表输出"""
        lines = [
            f"目录: {result['path']}",
            f"总计: {result['total_count']} 项",
            "-" * 60
        ]

        for entry in result["entries"]:
            type_icon = "📁" if entry["type"] == "directory" else "📄"
            size_str = f"{entry['size']:,} bytes" if entry["type"] == "file" else ""

            lines.append(
                f"{type_icon} {entry['name']:<30} {size_str:<15} {entry['modified']}"
            )

        return "\n".join(lines)

    def _format_file_info(self, info: dict) -> str:
        """格式化文件信息输出"""
        lines = [
            f"路径: {info['path']}",
            f"名称: {info['name']}",
            f"类型: {info['type']}",
            f"大小: {info['size']:,} bytes",
            f"修改时间: {info['modified']}",
        ]

        if "created" in info:
            lines.extend([
                f"创建时间: {info['created']}",
                f"访问时间: {info['accessed']}",
                f"权限: {info['permissions']}",
                f"可读: {'是' if info['readable'] else '否'}",
                f"可写: {'是' if info['writable'] else '否'}",
                f"可执行: {'是' if info['executable'] else '否'}",
            ])

            if info["type"] == "file" and "extension" in info:
                lines.append(f"扩展名: {info['extension']}")
            elif info["type"] == "directory" and "item_count" in info:
                lines.append(f"包含项目: {info['item_count']}")

        return "\n".join(lines)

    def _format_access_info(self, info: dict) -> str:
        """格式化访问权限信息输出"""
        lines = [
            f"路径: {info['path']}",
            f"存在: {'是' if info['exists'] else '否'}",
            f"安全检查: {'通过' if info['security_allowed'] else '失败'}",
        ]

        if not info["security_allowed"]:
            lines.append(f"安全原因: {info['security_reason']}")

        if info["exists"]:
            lines.extend([
                f"类型: {info.get('type', '未知')}",
                f"可读: {'是' if info['readable'] else '否'}",
                f"可写: {'是' if info['writable'] else '否'}",
                f"可执行: {'是' if info['executable'] else '否'}",
            ])

        return "\n".join(lines)

    async def run(self):
        """运行MCP服务器"""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="directory-browser",
                    server_version="0.1.0",
                    capabilities=self.server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    ),
                ),
            )


async def main():
    """主函数"""
    # 查找配置文件
    config_path = None
    possible_configs = [
        "config.json",
        Path(__file__).parent.parent.parent / "config.json",
        Path.home() / ".directory_browser_mcp" / "config.json"
    ]

    for config_file in possible_configs:
        if Path(config_file).exists():
            config_path = str(config_file)
            break

    # 创建并运行服务器
    server = DirectoryBrowserServer(config_path)
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
