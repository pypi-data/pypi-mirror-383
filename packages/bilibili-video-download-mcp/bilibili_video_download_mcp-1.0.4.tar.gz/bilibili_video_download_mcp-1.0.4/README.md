# Video Download MCP Server

基于 you-get 的通用视频下载 MCP 服务器，支持 100+ 个视频平台的内容下载。

> **完全集成版本**：本项目已将 you-get 的核心功能完全集成，无需外部依赖 you-get 项目。

## 功能特性

- **查看视频信息**: 获取视频标题、大小、格式、时长等详细信息
- **下载视频**: 支持从多个平台下载视频文件
- **多平台支持**: 支持哔哩哔哩、YouTube、抖音、微博等100+平台
- **多种格式**: 支持 MP4、FLV、WebM、MP3 等多种视频和音频格式

## 支持的平台

### 国内平台
- 哔哩哔哩 (bilibili.com)
- 抖音 (douyin.com)
- 微博视频 (weibo.com)
- 腾讯视频 (v.qq.com)
- 爱奇艺 (iqiyi.com)
- 优酷 (youku.com)
- 网易云音乐 (music.163.com)
- 知乎视频 (zhihu.com)
- 快手 (kuaishou.com)

### 国外平台
- YouTube (youtube.com)
- Twitter (twitter.com)
- Instagram (instagram.com)
- TikTok (tiktok.com)
- Vimeo (vimeo.com)
- Facebook (facebook.com)
- Dailymotion (dailymotion.com)
- SoundCloud (soundcloud.com)

还有更多平台支持，详见 [you-get 官方文档](https://github.com/soimort/you-get)。

## 安装

### 前置要求
- Python 3.8+
- 网络连接

### 本地安装和使用
```bash
# 克隆或下载项目
cd video_download_mcp

# 安装依赖
uv sync

# 运行服务器
uv run python -m bilibili_video_download_mcp

# 或者直接在 Claude Desktop 中配置使用
```

## 配置

在 Claude Desktop 的配置文件中添加以下内容：

```json
{
  "mcpServers": {
    "video-download-mcp": {
      "name": "Video Download MCP",
      "type": "stdio",
      "description": "Universal video downloader supporting 100+ platforms including Bilibili, YouTube, Douyin, etc.",
      "isActive": true,
      "registryUrl": "",
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/your/video_download_mcp",
        "run",
        "python",
        "-m",
        "bilibili_video_download_mcp"
      ]
    }
  }
}
```

## 使用方法

### 工具列表

#### 1. get_video_info
获取视频的详细信息，包括标题、大小、格式等。

**参数:**
- `url`: 视频链接URL

**示例:**
```
get_video_info("https://www.bilibili.com/video/BV1xx411c7mu")
```

#### 2. download_video
下载视频到指定目录。

**参数:**
- `url`: 视频链接URL
- `output_dir`: 输出目录路径（可选，默认为临时目录）
 - `format`: 可选，指定清晰度/流ID（例如 `dash-flv360-AVC`，可先用 get_video_info 查看可用值）
 - `cookies_path`: 可选，浏览器导出的 cookies 文件路径（支持 720p 及以上清晰度时常需登录）

**示例:**
```
download_video("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "/Users/username/Downloads")
```

**指定清晰度并使用登录 cookies 示例:**
```
download_video(
  url="https://www.bilibili.com/video/BV1xx411c7mu",
  output_dir="/Users/username/Downloads",
  format="dash-flv720-AVC",
  cookies_path="/Users/username/Desktop/cookies.txt"
)
```

### 资源

#### video://info/{url}
获取指定URL视频的详细信息资源（URL需要进行URL编码）。

### 使用示例

1. **获取B站视频信息**:
   ```
   请使用 get_video_info 工具获取这个B站视频的信息：
   https://www.bilibili.com/video/BV1xx411c7mu
   ```

2. **下载YouTube视频**:
   ```
   请使用 download_video 工具下载这个YouTube视频到我的下载目录：
   https://www.youtube.com/watch?v=dQw4w9WgXcQ
   ```

3. **批量操作**:
   ```
   请先获取这些视频的信息，然后下载它们：
   - https://www.bilibili.com/video/BV1xx411c7mu
   - https://www.youtube.com/watch?v=dQw4w9WgXcQ
   ```

## 技术架构

本项目基于以下技术构建：
- **MCP (Model Context Protocol)**: 提供标准化的工具接口
- **you-get**: 核心视频下载引擎
- **FastMCP**: 快速构建MCP服务器
- **asyncio**: 异步处理支持

## 注意事项

1. **版权和法律**: 请确保您有权下载和使用相关视频内容，遵守各平台的使用条款
2. **网络连接**: 某些平台可能有地理限制或需要登录
3. **存储空间**: 下载大文件前请确保有足够的存储空间
4. **更新维护**: 建议定期更新 you-get 以支持最新的平台变化

## 开发

### 本地开发
1. 克隆项目
2. 安装依赖: `pip install -e .`
3. 运行服务器: `python -m bilibili_video_download_mcp`

### 测试
```bash
python -m pytest tests/
```

## 许可证

MIT License - 详见 LICENSE 文件

## 贡献

欢迎提交 Issue 和 Pull Request！

## 更新日志

### v1.0.0
- 初始版本发布
- 支持视频信息获取和下载功能
- 支持100+视频平台

## 相关链接

- [you-get 官方项目](https://github.com/soimort/you-get)
- [MCP 协议文档](https://modelcontextprotocol.io/)
- [Claude Desktop](https://claude.ai/desktop)
