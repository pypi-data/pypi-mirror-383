# Youku Video Download MCP Server

基于 you-get 的优酷视频下载 MCP 服务器，专门用于优酷平台视频的获取和下载。

> **完全集成版本**：本项目已将 you-get 的核心功能完全集成，无需外部依赖 you-get 项目。

## 功能特性

- **查看优酷视频信息**: 获取优酷视频标题、大小、格式、时长等详细信息
- **下载优酷视频**: 支持从优酷平台下载视频文件
- **专门优化**: 专门针对优酷平台优化，支持多种优酷链接格式
- **多种格式**: 支持 MP4、FLV 等优酷视频格式

## 支持的优酷链接格式

- **视频页面**: https://v.youku.com/v_show/id_XXXXXX.html
- **播放器链接**: https://player.youku.com/player.php/sid/XXXXXX/v.swf
- **嵌入链接**: https://player.youku.com/embed/XXXXXX
- **节目列表**: https://list.youku.com/show/id_XXXXXX.html
- **专辑列表**: https://list.youku.com/albumlist/show/id_XXXXXX.html

## 支持的优酷视频格式

- **高清格式**: hd3 (1080P), hd2 (超清), mp4hd (高清)
- **标清格式**: mp4sd (标清), flv (标清)
- **容器格式**: MP4, FLV
- 自动选择最佳质量或指定格式下载

## 安装

### 前置要求
- Python 3.10+
- 网络连接

### 本地安装和使用
```bash
# 克隆或下载项目
cd youku_video_download_mcp

# 安装依赖
uv sync

# 运行服务器
uv run python -m youku_video_download_mcp.server

# 或者直接在 Claude Desktop 中配置使用
```

## 配置

在 Claude Desktop 的配置文件中添加以下内容：

```json
{
  "mcpServers": {
    "youku-video-download-mcp": {
      "name": "Youku Video Download MCP",
      "type": "stdio",
      "description": "Youku video downloader for downloading videos from Youku platform",
      "isActive": true,
      "registryUrl": "",
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/your/youku_video_download_mcp",
        "run",
        "python",
        "-m",
        "youku_video_download_mcp.server"
      ]
    }
  }
}
```

## 使用方法

### 工具列表

#### 1. get_video_info
获取优酷视频的详细信息，包括标题、大小、格式等。

**参数:**
- `url`: 优酷视频链接URL

**示例:**
```
get_video_info("https://v.youku.com/v_show/id_XNDQ5OTUxMjQ4.html")
```

#### 2. download_video
下载优酷视频到指定目录。

**参数:**
- `url`: 优酷视频链接URL
- `output_dir`: 输出目录路径（可选，默认为临时目录）
- `format`: 可选，指定清晰度/格式（例如 `hd3`, `hd2`, `mp4hd` 等）
- `cookies_path`: 可选，浏览器导出的 cookies 文件路径（用于登录获取更高清晰度）
- `merge`: 可选，是否合并视频片段（默认为True）

**示例:**
```
download_video("https://v.youku.com/v_show/id_XNDQ5OTUxMjQ4.html", "/Users/username/Downloads")
```

**指定清晰度并使用登录 cookies 示例:**
```
download_video(
  url="https://v.youku.com/v_show/id_XNDQ5OTUxMjQ4.html",
  output_dir="/Users/username/Downloads",
  format="hd3",
  cookies_path="/Users/username/Desktop/cookies.txt"
)
```

### 资源

#### youku://info/{url}
获取指定优酷视频URL的详细信息资源（URL需要进行URL编码）。

### 使用示例

1. **获取优酷视频信息**:
   ```
   请使用 get_video_info 工具获取这个优酷视频的信息：
   https://v.youku.com/v_show/id_XNDQ5OTUxMjQ4.html
   ```

2. **下载优酷视频**:
   ```
   请使用 download_video 工具下载这个优酷视频到我的下载目录：
   https://v.youku.com/v_show/id_XNDQ5OTUxMjQ4.html
   ```

3. **下载优酷节目列表**:
   ```
   请使用 download_video 工具下载这个优酷节目列表：
   https://list.youku.com/show/id_XXXXXX.html
   ```

## 技术架构

本项目基于以下技术构建：
- **MCP (Model Context Protocol)**: 提供标准化的工具接口
- **you-get**: 核心视频下载引擎（优酷模块）
- **FastMCP**: 快速构建MCP服务器
- **asyncio**: 异步处理支持

## 注意事项

1. **版权和法律**: 请确保您有权下载和使用相关优酷视频内容，遵守优酷的使用条款
2. **网络连接**: 优酷平台可能有地理限制或需要登录
3. **存储空间**: 下载大文件前请确保有足够的存储空间
4. **登录要求**: 某些高清视频可能需要登录优酷账号才能下载
5. **更新维护**: 建议定期更新以支持优酷平台的最新变化

## 开发

### 本地开发
1. 克隆项目
2. 安装依赖: `uv sync`
3. 运行服务器: `uv run python -m youku_video_download_mcp.server`

### 测试
```bash
uv run python -m pytest tests/
```

## 许可证

MIT License - 详见 LICENSE 文件

## 贡献

欢迎提交 Issue 和 Pull Request！

## 更新日志

### v1.0.0
- 初始版本发布
- 专门支持优酷视频下载
- 支持优酷视频信息获取和下载功能
- 支持多种优酷链接格式

## 相关链接

- [you-get 官方项目](https://github.com/soimort/you-get)
- [MCP 协议文档](https://modelcontextprotocol.io/)
- [Claude Desktop](https://claude.ai/desktop)
- [优酷官网](https://www.youku.com/)
