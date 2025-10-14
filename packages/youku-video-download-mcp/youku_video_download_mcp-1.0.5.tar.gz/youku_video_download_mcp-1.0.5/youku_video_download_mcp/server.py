#!/usr/bin/env python3
"""
优酷视频下载 MCP 服务器

该服务器基于 you-get 项目，专门用于优酷视频下载，提供以下功能：
1. 查看优酷视频信息 - 获取视频标题、大小、格式等信息
2. 下载优酷视频 - 下载优酷平台的视频内容
3. 仅支持优酷平台 - 专门针对优酷视频优化
"""

import os
import sys
import json
import tempfile
import socket
import asyncio
import io
import re
import traceback
from pathlib import Path
from typing import Optional, Dict, Any
from urllib.parse import urlparse
from contextlib import redirect_stdout, redirect_stderr

from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp import Context

# 导入 you-get 核心模块
from .you_get import common
from .you_get.common import any_download, print_info, url_to_module
from .you_get.util import log

# 创建 MCP 服务器实例
mcp = FastMCP("Youku Video Download MCP Server")


class VideoDownloadProcessor:
    """优酷视频下载处理器"""
    
    def __init__(self):
        self.temp_dir = Path(tempfile.mkdtemp(prefix="youku_video_download_"))
        # 设置 you-get 的全局参数
        common.dry_run = False
        common.json_output = False
        # 为所有网络请求设置默认超时，避免长时间阻塞导致 MCP 调用超时
        try:
            socket.setdefaulttimeout(10)
        except Exception:
            pass
    
    def _validate_youku_url(self, url: str) -> bool:
        """验证URL是否为优酷视频链接"""
        youku_patterns = [
            r'https?://v\.youku\.com/v_show/id_',
            r'https?://player\.youku\.com/player\.php/sid/',
            r'https?://loader\.swf\?VideoIDS=',
            r'https?://player\.youku\.com/embed/',
            r'https?://list\.youku\.com/show/id_',
            r'https?://list\.youku\.com/albumlist/show/id_'
        ]
        
        for pattern in youku_patterns:
            if re.search(pattern, url):
                return True
        return False
        
    def __del__(self):
        """清理临时目录"""
        import shutil
        if hasattr(self, 'temp_dir') and self.temp_dir.exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def _strip_ansi(self, text: str) -> str:
        """去除ANSI转义序列，确保输出为纯文本"""
        try:
            import re
            ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
            return ansi_escape.sub('', text)
        except Exception:
            return text
    
    def get_video_info(self, url: str) -> Dict[str, Any]:
        """获取优酷视频信息"""
        try:
            # 验证URL是否为优酷视频链接
            if not self._validate_youku_url(url):
                return {
                    "success": False,
                    "error": "仅支持优酷视频链接，请提供有效的优酷视频URL"
                }
            
            # 设置为信息模式
            original_dry_run = common.dry_run
            common.dry_run = True
            
            # 捕获输出
            output_buffer = io.StringIO()
            error_buffer = io.StringIO()
            
            try:
                with redirect_stdout(output_buffer), redirect_stderr(error_buffer):
                    # 获取模块和URL
                    module, processed_url = url_to_module(url)
                    
                    # 调用模块的download函数获取信息
                    module.download(processed_url, info_only=True)
                
                # 恢复原始设置
                common.dry_run = original_dry_run
                
                # 解析输出信息
                output = output_buffer.getvalue()
                info = self._parse_video_info(output)
                
                return {
                    "success": True,
                    "info": info,
                    "raw_output": output
                }
                
            except Exception as e:
                common.dry_run = original_dry_run
                error_output = error_buffer.getvalue()
                raise Exception(f"获取视频信息失败: {str(e)}\n{error_output}")
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _parse_video_info(self, output: str) -> Dict[str, Any]:
        """解析 you-get 输出的视频信息（兼容大小写与 streams 列表）"""
        info: Dict[str, Any] = {}
        output = self._strip_ansi(output)
        lines = [ln.rstrip() for ln in output.splitlines()]

        # 基础键（大小写不敏感）
        for raw in lines:
            line = raw.strip()
            lower = line.lower()
            if lower.startswith('site:'):
                info['site'] = line.split(':', 1)[1].strip()
            elif lower.startswith('title:'):
                info['title'] = line.split(':', 1)[1].strip()
            elif lower.startswith('type:'):
                info['type'] = line.split(':', 1)[1].strip()
            elif lower.startswith('size:') and 'bytes' in lower:
                size_part = line.split(':', 1)[1].strip()
                try:
                    # 示例: "83.8 MiB (87892717 bytes)"
                    before, paren = size_part.split('(', 1)
                    mb_value = before.strip().split(' ')[0]
                    bytes_value = ''.join(ch for ch in paren.split(')')[0] if ch.isdigit())
                    info['size'] = {
                        'mb': float(mb_value),
                        'bytes': int(bytes_value)
                    }
                except Exception:
                    info['size_raw'] = size_part
            elif lower.startswith('real url:') or lower.startswith('real urls:'):
                url_part = line.split(':', 1)[1].strip()
                if url_part.startswith('[') and url_part.endswith(']'):
                    try:
                        info['download_urls'] = json.loads(url_part)
                    except Exception:
                        info['download_urls'] = [url_part]
                else:
                    info['download_urls'] = [url_part]

        # 解析 streams 区块
        streams: list[Dict[str, Any]] = []
        i = 0
        while i < len(lines):
            if lines[i].strip().lower().startswith('streams:'):
                i += 1
                current: Dict[str, Any] = {}
                while i < len(lines):
                    ln = lines[i]
                    s = ln.strip()
                    if s == '' or s.startswith('#'):
                        i += 1
                        continue
                    if s.startswith('- '):
                        # 新条目开始，先推入旧的
                        if current:
                            streams.append(current)
                            current = {}
                        # "- format: dash-flv480-AVC"
                        if ':' in s:
                            key, val = s[2:].split(':', 1)
                            current[key.strip().lower()] = val.strip()
                        i += 1
                        continue
                    # 子项键值，如 "container: mp4"
                    if ':' in s:
                        key, val = s.split(':', 1)
                        current[key.strip().lower()] = val.strip()
                        # 尝试解析 size
                        if key.strip().lower() == 'size':
                            size_text = val.strip()
                            try:
                                if '(' in size_text and ')' in size_text:
                                    before, paren = size_text.split('(', 1)
                                    mb_value = before.strip().split(' ')[0]
                                    bytes_value = ''.join(ch for ch in paren.split(')')[0] if ch.isdigit())
                                    current['size_parsed'] = {
                                        'mb': float(mb_value),
                                        'bytes': int(bytes_value)
                                    }
                            except Exception:
                                pass
                        i += 1
                        continue
                    # 碰到空行或非缩进行，认为 streams 结束
                    if not ln.startswith(' '):
                        break
                    i += 1
                # 结束块时推入最后一个
                if current:
                    streams.append(current)
                # 不回退 i，这样可继续扫描后续内容
            else:
                i += 1

        if streams:
            info['streams'] = streams

        return info
    
    async def download_video(self, url: str, output_dir: Optional[str] = None, selected_format: Optional[str] = None, cookies_path: Optional[str] = None, merge: Optional[bool] = None, ctx: Context = None) -> Dict[str, Any]:
        """下载优酷视频"""
        try:
            # 验证URL是否为优酷视频链接
            if not self._validate_youku_url(url):
                return {
                    "success": False,
                    "error": "仅支持优酷视频链接，请提供有效的优酷视频URL"
                }
            
            if output_dir is None:
                # 默认下载到桌面
                output_dir = os.path.expanduser("~/Desktop")
            else:
                # 展开 ~ 与环境变量，标准化为绝对路径
                output_dir = os.path.abspath(os.path.expanduser(os.path.expandvars(output_dir)))
            
            if ctx:
                ctx.info(f"开始下载视频: {url}")
                ctx.info(f"下载目录: {output_dir}")
            
            # 确保输出目录存在
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            # 记录下载前的文件列表
            files_before = set(output_path.iterdir()) if output_path.exists() else set()
            
            # 设置下载参数
            original_dry_run = common.dry_run
            common.dry_run = False
            
            # 捕获输出
            output_buffer = io.StringIO()
            error_buffer = io.StringIO()
            
            try:
                with redirect_stdout(output_buffer), redirect_stderr(error_buffer):
                    # 获取模块和URL
                    module, processed_url = url_to_module(url)
                    
                    # 如果提供 cookies 路径，加载登录 cookies 以支持更高清晰度
                    if cookies_path:
                        try:
                            cp = os.path.expanduser(os.path.expandvars(cookies_path))
                            common.load_cookies(cp)
                            if ctx:
                                ctx.info(f"已加载 cookies: {cp}")
                        except Exception as e:
                            if ctx:
                                ctx.warn(f"加载 cookies 失败: {e}")

                    # 规范化用户传入的 format，去除ANSI转义并裁剪空白
                    if selected_format:
                        selected_format = self._strip_ansi(selected_format).strip()
                    # 在真正下载之前，若用户指定了 format，则预先做一次 info-only 获取可用清晰度，进行校验
                    if selected_format:
                        try:
                            info_out = io.StringIO()
                            info_err = io.StringIO()
                            with redirect_stdout(info_out), redirect_stderr(info_err):
                                module.download(processed_url, info_only=True)
                            info_parsed = self._parse_video_info(info_out.getvalue())
                            available_streams = []
                            if isinstance(info_parsed, dict) and isinstance(info_parsed.get('streams'), list):
                                for s in info_parsed['streams']:
                                    # you-get 输出里我们在 _parse_video_info 中将键统一为小写，并把格式放在 key 'format'
                                    fmt = s.get('format')
                                    if fmt:
                                        fmt = self._strip_ansi(fmt).strip()
                                        available_streams.append(fmt)
                            if available_streams and selected_format not in available_streams:
                                raise Exception(
                                    f"指定的 format 不可用: {selected_format}. 可用选项: {', '.join(available_streams)}"
                                )
                        except Exception as ve:
                            # 如果预检异常，向上抛出更友好的错误信息
                            raise

                    # 调用模块的 download 函数进行下载
                    # 未显式传入 merge 时，默认合并（更符合直觉，避免分轨输出）
                    kwargs = {"output_dir": output_dir, "merge": True if merge is None else bool(merge)}
                    if selected_format:
                        # you-get 使用 stream_id 指定清晰度/格式，例如 dash-flv360-AVC
                        kwargs["stream_id"] = selected_format
                    module.download(processed_url, **kwargs)
                
                # 恢复原始设置
                common.dry_run = original_dry_run
                
                # 查找新下载的文件
                files_after = set(output_path.iterdir()) if output_path.exists() else set()
                new_files = files_after - files_before
                downloaded_files = [str(f) for f in new_files if f.is_file()]
                
                if ctx:
                    ctx.info(f"下载完成！文件保存在: {output_dir}")
                    for file_path in downloaded_files:
                        ctx.info(f"下载文件: {Path(file_path).name}")
                
                return {
                    "success": True,
                    "output_dir": output_dir,
                    "downloaded_files": downloaded_files,
                    "raw_output": output_buffer.getvalue()
                }
                
            except Exception as e:
                common.dry_run = original_dry_run
                error_output = error_buffer.getvalue()
                raise Exception(f"下载失败: {str(e)}\n{error_output}")
            
        except Exception as e:
            if ctx:
                ctx.error(f"下载过程中出现错误: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }


@mcp.tool()
def get_video_info(url: str) -> str:
    """
    获取优酷视频信息
    
    参数:
    - url: 优酷视频链接URL
    
    返回:
    - 包含优酷视频信息的JSON字符串（标题、大小、格式等）
    
    支持的优酷链接格式：
    - https://v.youku.com/v_show/id_XXXXXX.html
    - https://player.youku.com/player.php/sid/XXXXXX/v.swf
    - https://player.youku.com/embed/XXXXXX
    - https://list.youku.com/show/id_XXXXXX.html
    - https://list.youku.com/albumlist/show/id_XXXXXX.html
    """
    try:
        processor = VideoDownloadProcessor()
        result = processor.get_video_info(url)

        if result["success"]:
            return json.dumps({
                "status": "success",
                "url": url,
                **result["info"],
                "message": "视频信息获取成功"
            }, ensure_ascii=False, indent=2)
        else:
            raise Exception(f"获取视频信息失败: {result['error']}")

    except Exception as e:
        # 抛出异常让 MCP 标记 isError=true
        raise


@mcp.tool()
async def download_video(
    url: str,
    output_dir: Optional[str] = None,
    format: Optional[str] = None,
    cookies_path: Optional[str] = None,
    merge: Optional[bool] = None,
    ctx: Context = None
) -> str:
    """
    下载优酷视频
    
    参数:
    - url: 优酷视频链接URL
    - output_dir: 输出目录路径（可选，默认为桌面）
    - format: 视频格式/清晰度（可选，如：hd3, hd2, mp4hd等）
    - cookies_path: cookies文件路径（可选，用于登录获取更高清晰度）
    - merge: 是否合并视频片段（可选，默认为True）
    
    返回:
    - 包含下载结果的JSON字符串
    
    支持的优酷链接格式：
    - https://v.youku.com/v_show/id_XXXXXX.html
    - https://player.youku.com/player.php/sid/XXXXXX/v.swf
    - https://player.youku.com/embed/XXXXXX
    - https://list.youku.com/show/id_XXXXXX.html
    - https://list.youku.com/albumlist/show/id_XXXXXX.html
    """
    try:
        processor = VideoDownloadProcessor()
        result = await processor.download_video(url, output_dir, selected_format=format, cookies_path=cookies_path, merge=merge, ctx=ctx)

        if result["success"]:
            return json.dumps({
                "status": "success",
                "url": url,
                "output_dir": result["output_dir"],
                "downloaded_files": result["downloaded_files"],
                "file_count": len(result["downloaded_files"]),
                "message": "视频下载成功"
            }, ensure_ascii=False, indent=2)
        else:
            raise Exception(result["error"])  # 让 MCP 标记 isError=true

    except Exception as e:
        if ctx:
            ctx.error(f"下载过程中出现错误: {str(e)}")
        # 抛出异常让 MCP 标记 isError=true
        raise


@mcp.resource("youku://info/{url}")
def get_video_resource(url: str) -> str:
    """
    获取指定优酷视频URL的详细信息资源
    
    参数:
    - url: 优酷视频URL（需要URL编码）
    
    返回:
    - 优酷视频详细信息
    """
    try:
        from urllib.parse import unquote
        decoded_url = unquote(url)
        processor = VideoDownloadProcessor()
        result = processor.get_video_info(decoded_url)
        
        if result["success"]:
            return json.dumps(result["info"], ensure_ascii=False, indent=2)
        else:
            return f"获取视频信息失败: {result['error']}"
    except Exception as e:
        return f"获取视频资源失败: {str(e)}"


@mcp.prompt()
def youku_video_download_guide() -> str:
    """优酷视频下载MCP服务使用指南"""
    return """
# 优酷视频下载MCP服务使用指南

## 功能说明
这个MCP服务器专门用于优酷视频下载，基于you-get项目，提供优酷视频的获取和下载功能。

## 支持的优酷链接格式
- **视频页面**: https://v.youku.com/v_show/id_XXXXXX.html
- **播放器链接**: https://player.youku.com/player.php/sid/XXXXXX/v.swf
- **嵌入链接**: https://player.youku.com/embed/XXXXXX
- **节目列表**: https://list.youku.com/show/id_XXXXXX.html
- **专辑列表**: https://list.youku.com/albumlist/show/id_XXXXXX.html

## 工具说明
- `get_video_info`: 获取优酷视频信息（标题、大小、格式等）
- `download_video`: 下载优酷视频文件到指定目录
- `youku://info/{url}`: 获取指定优酷视频URL的详细信息资源

## 使用示例

### 获取优酷视频信息
```
使用 get_video_info 工具，传入优酷视频URL：
- https://v.youku.com/v_show/id_XNDQ5OTUxMjQ4.html
- https://player.youku.com/embed/XNDQ5OTUxMjQ4
```

### 下载优酷视频
```
使用 download_video 工具：
- url: 优酷视频链接
- output_dir: 下载目录（可选，默认为桌面）
- format: 视频格式/清晰度（可选，如：hd3, hd2, mp4hd等）
- cookies_path: cookies文件路径（可选，用于登录获取更高清晰度）
```

## Claude Desktop 配置示例
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

## 注意事项
- 仅支持优酷平台的视频下载
- 请遵守优酷的使用条款和版权规定
- 某些视频可能需要登录才能获取更高清晰度
- 下载大文件时请确保网络连接稳定

## 支持的优酷视频格式
- **高清格式**: hd3 (1080P), hd2 (超清), mp4hd (高清)
- **标清格式**: mp4sd (标清), flv (标清)
- **容器格式**: MP4, FLV
- 自动选择最佳质量或指定格式下载

## 技术特性
- 专门针对优酷平台优化
- 支持多种优酷链接格式
- 自动格式检测
- 进度显示
- 支持登录获取更高清晰度
- 支持批量下载（节目列表、专辑列表）
"""


def main():
    """启动MCP服务器"""
    mcp.run()


if __name__ == "__main__":
    main()