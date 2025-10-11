# Cursor IDE 集成指南

## 📋 概述

本文档说明如何将 Pixverse MCP 服务器集成到 Cursor IDE 中，实现 AI 视频生成功能的无缝使用。

## 🔧 集成配置

### 全局 MCP 配置

Pixverse MCP 已配置在全局 MCP 配置文件中：`~/.cursor/mcp.json`

```json
{
  "mcpServers": {
    "pixverse": {
      "command": "/Users/jolsnow/pixverse_platform/pixverse_mcp/venv/bin/python",
      "args": [
        "/Users/jolsnow/pixverse_platform/pixverse_mcp/run_server.py",
        "--config",
        "/Users/jolsnow/pixverse_platform/pixverse_mcp/config.yaml"
      ],
      "env": {
        "PIXVERSE_API_KEY": "your_actual_api_key_here"
      }
    }
  }
}
```

### 配置说明

- **command**: 使用项目虚拟环境中的 Python 解释器
- **args**: 启动 MCP 服务器的参数
- **env**: 环境变量，包含 API 密钥

### 🎯 **用户配置重点**

**用户只需要修改一个地方：**
```json
"env": {
  "PIXVERSE_API_KEY": "替换为您的实际API密钥"
}
```

**说明：**
- ✅ `PIXVERSE_API_KEY` - 必需，替换为您的实际 API 密钥
- ✅ `PIXVERSE_BASE_URL` - 无需配置，已在 MCP 程序的 config.yaml 中设置
- ✅ 其他配置 - 无需配置，MCP 程序中已有合理默认值

## 🚀 使用方法

### 在 Cursor 中调用

1. **启动 Cursor IDE**
2. **确认 MCP 连接状态**（绿灯表示正常）
3. **在对话中直接使用**：

```
帮我生成一个视频：美丽的日落海景
```

```
用这张图片生成视频：/path/to/image.jpg
```

```
延长这个视频，添加更多动作场景
```

### 可用功能

- ✅ **文本生成视频** - 根据描述生成视频
- ✅ **图片生成视频** - 基于图片创建动态视频
- ✅ **视频延长** - 扩展现有视频内容
- ✅ **转场视频** - 创建图片间的平滑过渡
- ✅ **唇语同步** - 为视频添加语音和对口型
- ✅ **音效添加** - 为视频添加背景音效
- ✅ **状态查询** - 实时跟踪生成进度

## 🎯 最佳实践

### 1. 视频生成提示词

**推荐格式**：
```
生成视频：[主体描述] + [动作/场景] + [风格要求]

示例：
- "一只可爱的猫咪在花园里追逐蝴蝶，温暖的阳光，电影级画质"
- "现代都市夜景，霓虹灯闪烁，车流穿梭，赛博朋克风格"
```

### 2. 图片处理

**支持格式**：jpg, jpeg, png, webp
**建议尺寸**：推荐使用高质量图片获得更好效果

### 3. 轮询机制

- 系统会自动每2秒查询一次生成状态
- 超时时间设置为2分钟
- 生成完成后会自动显示结果

## 🔍 状态指示

### MCP 连接状态

- 🟢 **绿灯**：连接正常，可以使用
- 🔴 **红灯**：连接异常，需要检查配置
- 🟡 **黄灯**：连接中，请稍等

### 视频生成状态

- **pending**：任务已提交，等待处理
- **processing**：正在生成中
- **completed**：生成完成
- **failed**：生成失败

## 🛠️ 故障排除

### 常见问题

1. **MCP 显示红灯**
   ```bash
   # 检查虚拟环境
   source /Users/jolsnow/pixverse_platform/pixverse_mcp/venv/bin/activate
   
   # 测试服务器启动
   python run_server.py --config config.yaml
   ```

2. **API 调用失败**
   - 检查 API 密钥是否有效
   - 确认网络连接正常
   - 验证 base_url 是否正确

3. **生成超时**
   - 复杂视频可能需要更长时间
   - 可以稍后使用 get_video_status 查询结果

### 重新连接 MCP

如果遇到问题，可以在 Cursor 中：
1. 断开 MCP 连接
2. 重新连接
3. 确认状态变为绿灯

## 📈 性能优化

### 1. 批量处理

避免同时提交多个视频生成任务，建议串行处理。

### 2. 文件管理

- 上传的图片和视频会获得唯一 ID
- 可以重复使用已上传的媒体文件
- 定期清理不需要的临时文件

### 3. 网络优化

- 使用稳定的网络连接
- 避免在网络高峰期进行大量操作

## 📚 相关文档

- [配置指南](./CONFIGURATION_GUIDE.md) - 详细配置说明
- [README.md](./README.md) - 项目概述和快速开始
- [examples/](./examples/) - 使用示例代码

## 🔄 更新和维护

### 更新 MCP 服务器

```bash
cd /Users/jolsnow/pixverse_platform/pixverse_mcp
git pull origin main
pip install -r requirements.txt
```

### 重启服务

修改配置后需要在 Cursor 中重新连接 MCP 以生效。

---

*集成完成后，您就可以在 Cursor 中直接使用 AI 视频生成功能了！*
