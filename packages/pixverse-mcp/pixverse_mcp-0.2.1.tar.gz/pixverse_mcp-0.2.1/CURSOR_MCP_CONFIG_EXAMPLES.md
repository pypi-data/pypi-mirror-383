# Cursor MCP 配置示例

在 Cursor 中使用 pixverse-mcp 的不同配置方式：

## 🚀 方式 1: 使用 uvx + 指定版本（推荐）

```json
{
  "mcpServers": {
    "pixverse": {
      "command": "uvx",
      "args": [
        "pixverse-mcp==0.1.2"
      ],
      "env": {
        "PIXVERSE_API_KEY": "sk-your-api-key-here"
      }
    }
  }
}
```

**优点**：
- ✅ 自动管理依赖和环境
- ✅ 指定版本，确保稳定性
- ✅ 无需本地安装
- ✅ 跨平台兼容

## 🔄 方式 2: 使用 uvx + 最新版本

```json
{
  "mcpServers": {
    "pixverse": {
      "command": "uvx",
      "args": [
        "pixverse-mcp"
      ],
      "env": {
        "PIXVERSE_API_KEY": "sk-your-api-key-here"
      }
    }
  }
}
```

**优点**：
- ✅ 总是使用最新版本
- ✅ 自动获取更新

**注意**：
- ⚠️ 可能因版本更新导致不兼容

## 📁 方式 3: 使用本地开发版本

```json
{
  "mcpServers": {
    "pixverse": {
      "command": "uvx",
      "args": [
        "--from",
        "/Users/jolsnow/pixverse_platform/pixverse_mcp",
        "pixverse-mcp"
      ],
      "env": {
        "PIXVERSE_API_KEY": "sk-your-api-key-here"
      }
    }
  }
}
```

**适用场景**：
- 🔧 开发和调试
- 🧪 测试新功能
- 📝 本地修改

## ⚙️ 方式 4: 使用配置文件

```json
{
  "mcpServers": {
    "pixverse": {
      "command": "uvx",
      "args": [
        "pixverse-mcp==0.1.2",
        "--config",
        "/Users/jolsnow/mcp_dev_tools/config.yaml"
      ]
    }
  }
}
```

**配置文件内容** (`config.yaml`)：
```yaml
base_url: "https://app-api.pixverseai.cn"
api_key: "sk-your-api-key-here"
timeout: 30
max_retries: 3
```

## 🌐 方式 5: SSE 服务器模式

```json
{
  "mcpServers": {
    "pixverse": {
      "command": "uvx",
      "args": [
        "pixverse-mcp==0.1.2",
        "--sse",
        "--port",
        "8080"
      ],
      "env": {
        "PIXVERSE_API_KEY": "sk-your-api-key-here"
      }
    }
  }
}
```

**注意**：SSE 模式主要用于 Web 集成，MCP 通常使用 STDIO 模式。

## 🔧 方式 6: 传统 Python 方式（备用）

```json
{
  "mcpServers": {
    "pixverse": {
      "command": "python",
      "args": [
        "-m",
        "pixverse_mcp"
      ],
      "env": {
        "PIXVERSE_API_KEY": "sk-your-api-key-here"
      }
    }
  }
}
```

**前提**：需要先安装 `pip install pixverse-mcp`

## 📋 完整配置示例

```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["@playwright/mcp@latest"]
    },
    "context7": {
      "command": "npx", 
      "args": ["-y", "@upstash/context7-mcp"]
    },
    "fetch": {
      "command": "uvx",
      "args": ["mcp-server-fetch"]
    },
    "pixverse": {
      "command": "uvx",
      "args": ["pixverse-mcp==0.1.2"],
      "env": {
        "PIXVERSE_API_KEY": "sk-your-api-key-here"
      }
    }
  },
  "approvedProjectMcpServers": ["pixverse"],
  "disabledMcpServers": []
}
```

## 🎯 推荐配置

**生产使用**：
```json
"pixverse": {
  "command": "uvx",
  "args": ["pixverse-mcp==0.1.2"],
  "env": {
    "PIXVERSE_API_KEY": "sk-your-api-key-here"
  }
}
```

**开发调试**：
```json
"pixverse": {
  "command": "uvx",
  "args": [
    "--from",
    "/path/to/your/pixverse_mcp",
    "pixverse-mcp"
  ],
  "env": {
    "PIXVERSE_API_KEY": "your-api-key-here"
  }
}
```

## 🔐 安全提示

1. **API Key 管理**：
   - 不要在公共仓库中提交真实的 API Key
   - 考虑使用环境变量或配置文件
   - 定期轮换 API Key

2. **版本锁定**：
   - 生产环境建议指定具体版本
   - 测试新版本后再升级

3. **权限控制**：
   - 在 `approvedProjectMcpServers` 中添加 `"pixverse"`
   - 根据需要配置 `disabledMcpServers`
