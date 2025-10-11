# Pixverse MCP 安装和使用示例

## 🚀 快速开始

### 方式 1: 使用 uvx（推荐）

```bash
# 一键运行最新版本
uvx pixverse-mcp --help

# 指定版本运行
uvx pixverse-mcp==0.1.1 --help
```

### 方式 2: 使用 pip 安装

```bash
# 安装
pip install pixverse-mcp

# 运行
pixverse-mcp --help
```

## 📋 版本管理

### 指定具体版本

```bash
# uvx 方式
uvx pixverse-mcp==0.1.1 --config config.yaml

# pip 方式
pip install pixverse-mcp==0.1.1
```

### 版本范围

```bash
# 安装 0.1.x 系列的最新版本
pip install "pixverse-mcp>=0.1.0,<0.2.0"

# 安装大于等于 0.1.1 的版本
pip install "pixverse-mcp>=0.1.1"
```

### 查看可用版本

```bash
# 查看所有可用版本
pip index versions pixverse-mcp

# 或访问 PyPI 页面
# https://pypi.org/project/pixverse-mcp/#history
```

## 🌐 运行模式示例

### STDIO 模式（MCP 标准）

```bash
# 使用 uvx
uvx pixverse-mcp==0.1.1 --config config.yaml

# 使用已安装的版本
pixverse-mcp --config config.yaml
```

### SSE 服务器模式

```bash
# 启动 Web 服务器
uvx pixverse-mcp==0.1.1 --config config.yaml --sse --port 8080

# 访问 http://localhost:8080
```

## ⚙️ 配置文件

### 创建配置文件

```bash
# 下载配置模板
curl -O https://raw.githubusercontent.com/your-repo/pixverse-mcp/main/config.template.yaml

# 重命名并编辑
mv config.template.yaml config.yaml
# 编辑 config.yaml，填入您的 API key
```

### 配置内容示例

```yaml
# config.yaml
base_url: "https://app-api.pixverseai.cn"
api_key: "sk-your-api-key-here"
timeout: 30
max_retries: 3
```

## 🔧 环境变量方式

```bash
# 设置环境变量
export PIXVERSE_API_KEY="sk-your-api-key-here"

# 直接运行（无需配置文件）
uvx pixverse-mcp==0.1.1
```

## 📱 在不同环境中使用

### Docker 环境

```dockerfile
FROM python:3.12-slim

# 安装 uvx
RUN pip install uv

# 运行 pixverse-mcp
CMD ["uvx", "pixverse-mcp==0.1.1", "--config", "/app/config.yaml", "--sse", "--port", "8080"]
```

### GitHub Actions

```yaml
- name: Install and run pixverse-mcp
  run: |
    pip install uv
    uvx pixverse-mcp==0.1.1 --help
```

### 虚拟环境

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装
pip install pixverse-mcp==0.1.1

# 运行
pixverse-mcp --config config.yaml
```

## 🆙 升级和卸载

### 升级

```bash
# pip 方式
pip install --upgrade pixverse-mcp

# uv 方式
uv tool upgrade pixverse-mcp

# uvx 会自动使用最新版本
uvx pixverse-mcp --help  # 总是使用最新版本
```

### 卸载

```bash
# pip 方式
pip uninstall pixverse-mcp

# uv 方式
uv tool uninstall pixverse-mcp
```

## 🔍 故障排除

### 检查安装版本

```bash
# 查看已安装版本
pip show pixverse-mcp

# 或运行时查看
pixverse-mcp --version  # 如果支持的话
```

### 常见问题

1. **版本冲突**
   ```bash
   pip install --force-reinstall pixverse-mcp==0.1.1
   ```

2. **权限问题**
   ```bash
   pip install --user pixverse-mcp
   ```

3. **网络问题**
   ```bash
   pip install -i https://pypi.org/simple/ pixverse-mcp
   ```

## 📚 更多资源

- [PyPI 项目页面](https://pypi.org/project/pixverse-mcp/)
- [GitHub 仓库](https://github.com/your-username/pixverse-mcp)
- [完整文档](./README.md)
- [配置指南](./CONFIGURATION_GUIDE.md)
