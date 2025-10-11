"""Security module for access control"""

import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional


class SecurityManager:
    """安全管理器，负责访问控制和路径验证"""

    def __init__(self, config_path: Optional[str] = None):
        """
        初始化安全管理器

        Args:
            config_path: 配置文件路径（已弃用，现在使用内置配置）
        """
        # 直接使用内置配置
        import platform

        # 根据操作系统设置默认允许目录
        if platform.system() == "Windows":
            # Windows系统：允许访问所有盘符
            self.allowed_directories: List[str] = [
                "C:\\", "D:\\", "E:\\", "F:\\", "G:\\", "H:\\",
                "C:/", "D:/", "E:/", "F:/", "G:/", "H:/"  # 支持正斜杠格式
            ]
        else:
            # Unix-like系统：允许访问根目录
            self.allowed_directories: List[str] = ["/"]

        self.show_hidden_files: bool = False
        self.max_entries: int = 1000

        if config_path:
            self.load_config(config_path)

    def load_config(self, config_path: str) -> bool:
        """
        加载配置文件

        Args:
            config_path: 配置文件路径

        Returns:
            是否加载成功
        """
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)

            self.allowed_directories = [
                str(Path(d).resolve()) for d in config.get('allowed_directories', [])
            ]
            self.show_hidden_files = config.get('show_hidden_files', False)
            self.max_entries = config.get('max_entries', 1000)

            return True

        except (FileNotFoundError, json.JSONDecodeError, Exception) as e:
            print(f"加载配置文件失败: {e}")
            # 使用内置默认配置（允许访问整个文件系统）
            self.allowed_directories = ["/"]
            return False

    def is_path_allowed(self, path: str) -> Dict[str, Any]:
        """
        检查路径是否被允许访问

        Args:
            path: 要检查的路径

        Returns:
            包含检查结果的字典
        """
        try:
            import platform

            # 规范化路径
            normalized_path = str(Path(path).resolve())

            # 检查路径穿越攻击
            if self._has_path_traversal(path):
                return {
                    "allowed": False,
                    "reason": "检测到路径穿越攻击",
                    "path": normalized_path
                }

            # Windows系统特殊处理
            if platform.system() == "Windows":
                # 统一转换为小写并使用正斜杠进行比较
                normalized_path_lower = normalized_path.lower().replace("\\", "/")

                # 检查是否在允许的目录中
                for allowed_dir in self.allowed_directories:
                    allowed_dir_lower = allowed_dir.lower().replace("\\", "/")

                    # 处理盘符格式（C:/ 或 C:\\）
                    if normalized_path_lower.startswith(allowed_dir_lower):
                        return {
                            "allowed": True,
                            "path": normalized_path,
                            "allowed_root": allowed_dir
                        }

                    # 检查是否是盘符路径（如 C:, D: 等）
                    if len(normalized_path_lower) >= 2 and normalized_path_lower[1] == ':':
                        drive_letter = normalized_path_lower[0:2]
                        if drive_letter + "/" in allowed_dir_lower or drive_letter + "\\" in allowed_dir_lower:
                            return {
                                "allowed": True,
                                "path": normalized_path,
                                "allowed_root": allowed_dir
                            }
            else:
                # Unix-like系统的处理
                for allowed_dir in self.allowed_directories:
                    if normalized_path.startswith(allowed_dir):
                        return {
                            "allowed": True,
                            "path": normalized_path,
                            "allowed_root": allowed_dir
                        }

            return {
                "allowed": False,
                "reason": "路径不在允许的目录范围内",
                "path": normalized_path,
                "allowed_directories": self.allowed_directories
            }

        except Exception as e:
            return {
                "allowed": False,
                "reason": f"路径验证失败: {str(e)}",
                "path": path
            }

    def validate_request(self, path: str, operation: str) -> Dict[str, Any]:
        """
        验证请求的安全性

        Args:
            path: 请求的路径
            operation: 操作类型 (list, info, check, open)

        Returns:
            验证结果
        """
        # 检查路径权限
        path_check = self.is_path_allowed(path)
        if not path_check["allowed"]:
            return {
                "valid": False,
                "error": path_check["reason"],
                "details": path_check
            }

        # 检查操作权限
        if operation not in ["list", "info", "check", "open"]:
            return {
                "valid": False,
                "error": f"不支持的操作: {operation}"
            }

        # 检查路径是否存在且可访问
        try:
            target_path = Path(path).resolve()
            if not target_path.exists():
                return {
                    "valid": False,
                    "error": f"路径不存在: {path}"
                }

            if not os.access(target_path, os.R_OK):
                return {
                    "valid": False,
                    "error": f"没有读取权限: {path}"
                }

            return {
                "valid": True,
                "path": str(target_path),
                "operation": operation
            }

        except Exception as e:
            return {
                "valid": False,
                "error": f"路径验证失败: {str(e)}"
            }

    def _has_path_traversal(self, path: str) -> bool:
        """
        检查路径是否包含路径穿越攻击

        Args:
            path: 要检查的路径

        Returns:
            是否包含路径穿越
        """
        # 检查常见的路径穿越模式
        dangerous_patterns = [
            '../',
            '..\\',
            '..',
            '//',
            '\\\\',
            '~/',
            '${'
        ]

        normalized_path = path.replace('\\', '/').lower()

        for pattern in dangerous_patterns:
            if pattern in normalized_path:
                return True

        return False

    def get_allowed_directories(self) -> List[str]:
        """
        获取允许访问的目录列表

        Returns:
            允许访问的目录列表
        """
        return self.allowed_directories.copy()

    def add_allowed_directory(self, directory: str) -> bool:
        """
        添加允许访问的目录

        Args:
            directory: 目录路径

        Returns:
            是否添加成功
        """
        try:
            normalized_dir = str(Path(directory).resolve())
            if normalized_dir not in self.allowed_directories:
                self.allowed_directories.append(normalized_dir)
                return True
            return False
        except Exception:
            return False

    def remove_allowed_directory(self, directory: str) -> bool:
        """
        移除允许访问的目录

        Args:
            directory: 目录路径

        Returns:
            是否移除成功
        """
        try:
            normalized_dir = str(Path(directory).resolve())
            if normalized_dir in self.allowed_directories:
                self.allowed_directories.remove(normalized_dir)
                return True
            return False
        except Exception:
            return False

    def get_config_summary(self) -> Dict[str, Any]:
        """
        获取配置摘要

        Returns:
            配置信息摘要
        """
        return {
            "allowed_directories": self.allowed_directories,
            "show_hidden_files": self.show_hidden_files,
            "max_entries": self.max_entries,
            "total_allowed_dirs": len(self.allowed_directories)
        }
