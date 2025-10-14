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
- 如果已发布到 PyPI（控制台脚本 `weather-mcp`），可在客户端直接使用 `uvx` 调用，无需克隆仓库：

```
{
  "mcpServers": {
    "weather": {
      "name": "weather",
      "type": "stdio",
      "command": "uvx",
      "args": [
        "weather-mcp"
      ],
      "env": {
        "QWEATHER_API_HOST": "your_api_host",
        "QWEATHER_API_KEY": "your_api_key"
      }
    }
  }
}
```

- 或者使用本地已安装的脚本入口（`pipx` 或 `uv pip install -e .` 后）：

```
{
  "mcpServers": {
    "weather": {
      "name": "weather",
      "type": "stdio",
      "command": "weather-mcp",
      "env": {
        "QWEATHER_API_HOST": "your_api_host",
        "QWEATHER_API_KEY": "your_api_key"
      }
    }
  }
}
```

说明：
- `uvx` 会临时拉取并运行已发布工具的控制台脚本，适合无需克隆的快速使用；
- 若尚未发布到 PyPI，可先克隆仓库后执行 `uv pip install -e .` 安装脚本入口；
- 服务会从环境变量或 `.env` 读取 `QWEATHER_API_HOST` 与 `QWEATHER_API_KEY`。

### GitHub Actions 自动发布
- 已内置工作流：`.github/workflows/publish.yml`
- 触发规则：
  - 推送到 `main` 分支：自动发布到 TestPyPI。
  - 推送符合 `v*` 的标签（如 `v0.1.1`）：自动发布到正式 PyPI。
- 推荐使用 Trusted Publishing：
  - 在 PyPI 项目设置启用“Trusted Publishers”，关联此 GitHub 仓库；启用后无需设置密钥。
- 若暂未配置 Trusted Publishing，可用密钥发布：
  - 在仓库 Secrets 添加 `TEST_PYPI_API_TOKEN` 与 `PYPI_API_TOKEN`（API Token）；
  - 工作流内已留注释，可切换为 `TWINE_USERNAME=__token__` 与对应密码的方式。

## 许可

未设置专有许可证。如需开源协议，请在 `pyproject.toml` 或根目录添加相应许可文件。
