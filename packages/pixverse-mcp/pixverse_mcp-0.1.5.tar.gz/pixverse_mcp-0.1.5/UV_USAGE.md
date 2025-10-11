# UV 使用指南

您的 pixverse_mcp 项目已经成功迁移到使用 uv 管理！

## 主要变化

1. **依赖管理**: 现在使用 `uv.lock` 文件锁定依赖版本，替代了 `requirements.txt`
2. **项目配置**: 更新了 `pyproject.toml` 以支持 uv 和 uvx
3. **入口点**: 添加了 `__main__.py` 文件作为 uvx 入口点

## 常用命令

### 开发环境

```bash
# 安装依赖并创建虚拟环境
uv sync

# 运行项目
uv run pixverse-mcp --help

# 运行 SSE 服务器
uv run pixverse-mcp --sse --port 8080

# 添加新依赖
uv add package-name

# 添加开发依赖
uv add --dev package-name

# 更新依赖
uv lock --upgrade
```

### 使用 uvx 运行

```bash
# 从本地目录运行
uvx --from . pixverse-mcp --help

# 从 Git 仓库运行（如果发布到 Git）
uvx --from git+https://github.com/your-repo/pixverse-mcp pixverse-mcp

# 从 PyPI 运行（如果发布到 PyPI）
uvx pixverse-mcp
```

### 构建和发布

```bash
# 构建包
uv build

# 发布到 PyPI（需要配置认证）
uv publish
```

## 项目结构

```
pixverse_mcp/
├── pyproject.toml          # 项目配置和依赖
├── uv.lock                 # 锁定的依赖版本
├── config.yaml             # MCP 配置
└── src/
    └── pixverse_mcp/
        ├── __init__.py
        ├── __main__.py     # uvx 入口点
        ├── server.py       # 主服务器代码
        └── ...
```

## 优势

- **更快的依赖解析**: uv 比 pip 快 10-100 倍
- **确定性构建**: uv.lock 确保所有环境使用相同的依赖版本
- **简化部署**: uvx 可以直接运行项目，无需手动安装
- **现代化工具链**: 基于 Rust 构建，性能优异

## 注意事项

- 确保系统已安装 uv: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- 如果需要在 CI/CD 中使用，建议使用 `uv sync --frozen` 确保使用锁定的版本
- 环境变量配置保持不变，仍需在 `~/.cursor/mcp.json` 中配置 `PIXVERSE_API_KEY`
