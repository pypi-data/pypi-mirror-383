# Weather MCP Server

一个基于 FastMCP 的和风天气（QWeather）查询服务，提供以下工具：

- `lookup_city(location)`: 城市/位置查询（名称或经纬度）
- `get_warning(location)`: 天气预警查询（LocationID 或经纬度）
- `get_forecast(location)`: 当前天气查询（LocationID 或经纬度）

## 安装与运行

- 克隆仓库：

```bash
git clone --depth 1 https://github.com/gandli/mcp-qweather
uv sync
```

- 在支持 MCP 的客户端中，可添加如下配置以 `stdio` 方式启动本服务：

```json
{
  "mcpServers": {
    "weather": {
      "name": "weather",
      "type": "stdio",
      "description": "一个基于 FastMCP 的和风天气（QWeather）查询服务",
      "isActive": true,
      "registryUrl": "",
      "command": "uv",
      "args": [
        "--directory",
        "path/to/mcp-qweather",
        "run",
        "main.py"
      ],
      "env": {
        "QWEATHER_API_HOST": "your_api_host",
        "QWEATHER_API_KEY": "your_api_key"
      }
    }
  }
}
```

### 零克隆使用（更省事的方式）
- 如果已发布到 PyPI（控制台脚本 `mcp-qweather`），可在客户端直接使用 `uvx` 调用，无需克隆仓库：

```
{
  "mcpServers": {
    "weather": {
      "name": "weather",
      "type": "stdio",
      "command": "uvx",
      "args": [
        "mcp-qweather"
      ],
      "env": {
        "QWEATHER_API_HOST": "your_api_host",
        "QWEATHER_API_KEY": "your_api_key"
      }
    }
  }
}
```

`QWEATHER_API_KEY`：前往[和风天气开发控制台](https://console.qweather.com/project?lang=zh)，创建项目并生成凭据，获取 API Key。
`QWEATHER_API_HOST`：前往[设置页·开发者信息](https://console.qweather.com/setting?lang=zh)，查看并复制 API Host。

## 许可

- 采用 MIT 许可证（见 `LICENSE`）。
- 已在 `pyproject.toml` 设置 `license = { file = "LICENSE" }` 与分类器。
