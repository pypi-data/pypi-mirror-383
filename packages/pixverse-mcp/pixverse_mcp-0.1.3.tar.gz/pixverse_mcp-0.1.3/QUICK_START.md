# Pixverse MCP 快速开始

## 🚀 一键运行

### 方式 1: 从 PyPI 运行（推荐）

```bash
# 直接运行（需要先发布到 PyPI）
uvx pixverse-mcp --help
```

### 方式 2: 从 Git 仓库运行

```bash
# 从 GitHub 运行
uvx --from git+https://github.com/your-username/pixverse-mcp pixverse-mcp --help
```

### 方式 3: 从本地运行

```bash
# 克隆项目
git clone https://github.com/your-username/pixverse-mcp
cd pixverse-mcp

# 运行
uvx --from . pixverse-mcp --help
```

## ⚙️ 配置 API Key

### 方法 1: 使用配置文件

```bash
# 1. 复制配置模板
cp config.template.yaml config.yaml

# 2. 编辑配置文件，填入您的 API Key
# api_key: "sk-your-actual-api-key"

# 3. 运行
uvx pixverse-mcp --config config.yaml
```

### 方法 2: 使用环境变量

```bash
# 设置环境变量
export PIXVERSE_API_KEY="sk-your-actual-api-key"

# 运行
uvx pixverse-mcp
```

## 🌐 运行模式

### STDIO 模式（MCP 标准）

```bash
uvx pixverse-mcp --config config.yaml
```

### SSE 服务器模式（Web API）

```bash
uvx pixverse-mcp --config config.yaml --sse --port 8080
```

然后访问：http://localhost:8080

## 📝 使用示例

### 1. 文本生成视频

```bash
# 启动 SSE 服务器
uvx pixverse-mcp --config config.yaml --sse --port 8080

# 然后通过 HTTP API 调用
curl -X POST http://localhost:8080/api/text-to-video \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "A cat playing in the garden",
    "duration": 5,
    "quality": "720p"
  }'
```

### 2. 图片生成视频

```bash
# 先上传图片，然后生成视频
curl -X POST http://localhost:8080/api/image-to-video \
  -H "Content-Type: application/json" \
  -d '{
    "img_id": 12345,
    "prompt": "Make the cat move and play",
    "duration": 5
  }'
```

## 🔧 故障排除

### 常见问题

1. **API Key 错误**
   ```
   Error: API key is required
   ```
   解决：检查配置文件中的 api_key 或环境变量 PIXVERSE_API_KEY

2. **端口被占用**
   ```
   Error: Port 8080 is already in use
   ```
   解决：使用不同端口 `--port 8081`

3. **网络连接问题**
   ```
   Error: Connection timeout
   ```
   解决：检查网络连接和防火墙设置

### 获取帮助

```bash
# 查看所有选项
uvx pixverse-mcp --help

# 查看版本信息
uvx pixverse-mcp --version
```

## 📚 更多资源

- [完整文档](./README.md)
- [配置指南](./CONFIGURATION_GUIDE.md)
- [Cursor 集成](./CURSOR_INTEGRATION.md)
- [UV 使用指南](./UV_USAGE.md)
- [分发指南](./DISTRIBUTION_GUIDE.md)
