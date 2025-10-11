# Directory Browser MCP Server

一个用于浏览目录和文件的MCP (Model Context Protocol) 服务器。

## 功能特性

- 📁 **目录浏览** - 列出指定目录的内容
- 📄 **文件信息** - 获取文件/目录的详细信息
- 🔍 **权限检查** - 检查路径的访问权限
- 🛡️ **安全控制** - 基于白名单的目录访问控制

## 安装

```bash
cd directory_browser_mcp
pip install -e .
```

## 配置

编辑 `config.json` 文件来配置允许访问的目录：

```json
{
  "allowed_directories": [
    "/Users/用户名/Documents",
    "/Users/用户名/Desktop",
    "/项目根目录"
  ],
  "show_hidden_files": false,
  "max_entries": 1000
}
```

## 使用方法

### 作为MCP服务器运行

```bash
python -m directory_browser_mcp
```

### 可用工具

1. **list_directory** - 列出目录内容
   - `path`: 目录路径
   - `show_hidden`: 是否显示隐藏文件 (可选)

2. **get_file_info** - 获取文件详细信息
   - `path`: 文件或目录路径

3. **check_path_access** - 检查路径访问权限
   - `path`: 要检查的路径

## 安全特性

- ✅ 白名单目录访问控制
- ✅ 路径穿越攻击防护
- ✅ 文件系统权限检查
- ✅ 安全错误处理

## 示例

```python
# 列出目录
{
  "tool": "list_directory",
  "arguments": {
    "path": "/Users/username/Documents",
    "show_hidden": false
  }
}

# 获取文件信息
{
  "tool": "get_file_info",
  "arguments": {
    "path": "/Users/username/Documents/file.txt"
  }
}

# 检查访问权限
{
  "tool": "check_path_access",
  "arguments": {
    "path": "/Users/username/Documents"
  }
}
```