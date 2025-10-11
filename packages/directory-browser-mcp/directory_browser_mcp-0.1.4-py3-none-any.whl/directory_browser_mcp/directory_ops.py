"""Directory operations module for MCP server"""

import os
import stat
import subprocess
import platform
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional


class DirectoryOperations:
    """Core directory and file operations"""

    def __init__(self):
        pass

    def list_directory(self, path: str, show_hidden: bool = False) -> Dict[str, Any]:
        """
        列出目录内容

        Args:
            path: 目录路径
            show_hidden: 是否显示隐藏文件

        Returns:
            包含目录内容信息的字典
        """
        try:
            target_path = Path(path).resolve()

            if not target_path.exists():
                return {"error": f"路径不存在: {path}"}

            if not target_path.is_dir():
                return {"error": f"不是目录: {path}"}

            entries = []

            for entry in target_path.iterdir():
                # 跳过隐藏文件（如果不显示）
                if not show_hidden and entry.name.startswith('.'):
                    continue

                try:
                    entry_info = self._get_entry_info(entry)
                    entries.append(entry_info)
                except (OSError, PermissionError):
                    # 跳过无法访问的文件
                    continue

            # 按类型和名称排序（目录在前）
            entries.sort(key=lambda x: (x['type'] != 'directory', x['name'].lower()))

            return {
                "path": str(target_path),
                "entries": entries,
                "total_count": len(entries)
            }

        except PermissionError:
            return {"error": f"没有访问权限: {path}"}
        except Exception as e:
            return {"error": f"列出目录失败: {str(e)}"}

    def get_file_info(self, path: str) -> Dict[str, Any]:
        """
        获取文件或目录的详细信息

        Args:
            path: 文件或目录路径

        Returns:
            包含文件信息的字典
        """
        try:
            target_path = Path(path).resolve()

            if not target_path.exists():
                return {"error": f"路径不存在: {path}"}

            info = self._get_entry_info(target_path, detailed=True)
            return info

        except PermissionError:
            return {"error": f"没有访问权限: {path}"}
        except Exception as e:
            return {"error": f"获取文件信息失败: {str(e)}"}

    def check_path_access(self, path: str) -> Dict[str, Any]:
        """
        检查路径访问权限

        Args:
            path: 路径

        Returns:
            包含访问权限信息的字典
        """
        try:
            target_path = Path(path).resolve()

            result = {
                "path": str(target_path),
                "exists": target_path.exists(),
                "readable": False,
                "writable": False,
                "executable": False
            }

            if target_path.exists():
                result["readable"] = os.access(target_path, os.R_OK)
                result["writable"] = os.access(target_path, os.W_OK)
                result["executable"] = os.access(target_path, os.X_OK)
                result["type"] = "directory" if target_path.is_dir() else "file"

            return result

        except Exception as e:
            return {"error": f"检查访问权限失败: {str(e)}"}

    def _get_entry_info(self, path: Path, detailed: bool = False) -> Dict[str, Any]:
        """获取文件或目录的基本信息"""
        try:
            stat_info = path.stat()

            entry_info = {
                "name": path.name,
                "path": str(path),
                "type": "directory" if path.is_dir() else "file",
                "size": stat_info.st_size,
                "modified": datetime.fromtimestamp(stat_info.st_mtime).isoformat()
            }

            if detailed:
                entry_info.update({
                    "created": datetime.fromtimestamp(stat_info.st_ctime).isoformat(),
                    "accessed": datetime.fromtimestamp(stat_info.st_atime).isoformat(),
                    "permissions": oct(stat_info.st_mode)[-3:],
                    "owner_uid": stat_info.st_uid,
                    "group_gid": stat_info.st_gid,
                    "readable": os.access(path, os.R_OK),
                    "writable": os.access(path, os.W_OK),
                    "executable": os.access(path, os.X_OK)
                })

                if path.is_file():
                    entry_info["extension"] = path.suffix.lower()
                elif path.is_dir():
                    try:
                        # 统计目录中的项目数量
                        item_count = len(list(path.iterdir()))
                        entry_info["item_count"] = item_count
                    except PermissionError:
                        entry_info["item_count"] = "无法访问"

            return entry_info

        except Exception as e:
            return {
                "name": path.name,
                "path": str(path),
                "error": f"获取信息失败: {str(e)}"
            }

    def open_directory(self, path: str) -> Dict[str, Any]:
        """
        打开目录（在系统文件管理器中）

        Args:
            path: 目录路径

        Returns:
            包含操作结果的字典
        """
        try:
            target_path = Path(path).resolve()

            if not target_path.exists():
                return {"error": f"路径不存在: {path}"}

            if not target_path.is_dir():
                return {"error": f"不是目录: {path}"}

            # 根据操作系统选择合适的命令
            system = platform.system().lower()

            if system == "darwin":  # macOS
                subprocess.run(["open", str(target_path)], check=True)
            elif system == "windows":  # Windows
                # Windows需要使用特殊的处理方式
                # 使用os.startfile或explorer命令
                import os
                try:
                    # 优先使用os.startfile，这是Windows推荐的方式
                    os.startfile(str(target_path))
                except AttributeError:
                    # 如果os.startfile不可用，使用explorer命令
                    # 确保路径格式正确（使用反斜杠）
                    windows_path = str(target_path).replace("/", "\\")
                    subprocess.run(["explorer", windows_path], check=True, shell=True)
            elif system == "linux":  # Linux
                # 尝试多种可能的文件管理器
                file_managers = ["xdg-open", "nautilus", "thunar", "dolphin", "pcmanfm"]
                for fm in file_managers:
                    try:
                        subprocess.run([fm, str(target_path)], check=True)
                        break
                    except (subprocess.CalledProcessError, FileNotFoundError):
                        continue
                else:
                    return {"error": "未找到可用的文件管理器"}
            else:
                return {"error": f"不支持的操作系统: {system}"}

            return {
                "success": True,
                "path": str(target_path),
                "message": f"已在系统文件管理器中打开目录: {target_path}"
            }

        except subprocess.CalledProcessError as e:
            return {"error": f"打开目录失败: {str(e)}"}
        except PermissionError:
            return {"error": f"没有访问权限: {path}"}
        except Exception as e:
            return {"error": f"打开目录失败: {str(e)}"}

    def _format_size(self, size_bytes: int) -> str:
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} PB"