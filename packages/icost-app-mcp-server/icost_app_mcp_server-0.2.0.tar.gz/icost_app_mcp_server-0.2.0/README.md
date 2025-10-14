# iCost App MCP Server

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![FastMCP](https://img.shields.io/badge/FastMCP-2.0-green.svg)](https://github.com/jlowin/fastmcp)
[![PyPI](https://img.shields.io/pypi/v/icost-app-mcp-server.svg)](https://pypi.org/project/icost-app-mcp-server/)
[![GitHub](https://img.shields.io/github/stars/TooLife/icost-app-mcp-server.svg?style=social&label=Star)](https://github.com/TooLife/icost-app-mcp-server)

一个基于 FastMCP 2.0 框架构建的模型上下文协议（MCP）服务，专为 iCost iOS 记账应用提供智能记账功能集成。

## 📖 使用示例
![使用](mcp-client.png)

![结果](icost-app.png)

## ✨ 功能特性

- 🏦 **多账户支持**: 支持支付宝、微信、银行卡等多种账户类型
- 💱 **多币种支持**: 支持人民币及其他主要货币
- 📊 **智能分类**: 提供完整的收入和支出分类系统
- 📱 **无缝集成**: 通过 URL Scheme 与 iCost 应用深度集成
- 🚀 **高性能**: 基于 FastMCP 2.0 和现代 Python async/await 模式
- 🛡️ **类型安全**: 完整的类型提示和数据验证
- 📝 **详细记录**: 支持备注、标签、位置等详细信息记录

## 🔧 核心功能

### 记账操作
- **添加支出记录** (`icost_add_expense`): 记录日常消费，支持多种分类如餐饮、购物、交通等
- **添加收入记录** (`icost_add_income`): 记录收入来源，如工资、奖金、投资收益等  
- **添加转账记录** (`icost_add_transfer`): 记录账户间资金转移

### 应用控制
- **打开应用页面** (`icost_open_app`): 快速跳转到 iCost 应用的特定功能页面
  - `asset_main`: 资产首页
  - `chart_main`: 统计首页
  - `quick_record`: 记账页面

### 智能分类
- **获取支持分类** (`icost_categories`): 提供完整的收入和支出分类列表

### 时间工具
- **当前时间** (`current_time`): 获取当前时间用于记账
- **时间快捷方式**: `am()`, `pm()`, `default_time()` 等便捷时间设置


## 🚀 快速开始

### 环境要求
- Python 3.10+
- macOS (用于 URL Scheme 集成)

### ⚙️ 配置选项

服务器支持以下配置参数：

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--transport` | stdio, http | 通信协议，默认stdio |
| `--host` | localhost | 服务器绑定主机 |
| `--port` | 9000 | 服务器端口 |
| `--debug` | False | 调试模式 |
| `--log-level` | INFO | 日志级别 |

### 一键安装运行配置

#### **最简单的一键命令（推荐）**

直接在 MCP Client 配置中使用安装并运行的命令：

**Claude Desktop/Cherry Studio...：**
```json
{
  "mcpServers": {
    "icost-app-mcp-server": {
      "command": "sh",
      "args": ["-c", "pip install --quiet icost-app-mcp-server && icost-app-mcp-server"]
    }
  }
}

// -- 方式2:本地已经install过
{
  "mcpServers": {
    "icost-app-mcp-server": {
      "command": "icost-app-mcp-server"
    }
  }
}

// -- 方式3
// bash
python icost-app-mcp-server --transport http --host localhost --port 9000
// mcp server config
{
   "mcpServers": {
      "icost-app-mcp-server": {
        "url": "http://localhost:9000"
      }
   }
}
```

#### **方式二：从 PyPI 安装**

```bash
# 安装最新版本
pip install icost-app-mcp-server

# 验证安装
icost-app-mcp-server --help

# 使用默认配置启动
icost-app-mcp-server

# 自定义主机和端口
icost-app-mcp-server --host 0.0.0.0 --port 8080

# 启用调试模式
icost-app-mcp-server --debug --log-level DEBUG
```


### 验证集成

集成成功后，您应该能在 MCP Client 中看到以下工具：

- `icost_add_expense` - 添加支出记录
- `icost_add_income` - 添加收入记录  
- `icost_add_transfer` - 添加转账记录
- `icost_open_app` - 打开 iCost 应用页面
- `icost_categories` - 获取支持的分类
- `current_time` - 获取当前时间


## 📋 支持的分类

### 支出分类
餐饮、购物、交通、日用、通讯、住房、医疗、医疗健康、服饰、数码电器、汽车、学习、办公、运动、社交、人情、育儿、母婴亲子、旅行、烟酒、扫二维码付款、充值缴费、生活服务、文化休闲、理财、水果、其他

### 收入分类
工资、奖金、福利、退款、红包、副业、退税、投资、其他

## 🤝 贡献指南

我们欢迎各种形式的贡献！请查看 [贡献指南](CONTRIBUTING.md) 了解详细信息。


## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🔗 相关链接

- **PyPI 包页面**: https://pypi.org/project/icost-app-mcp-server/
- **项目主页**: https://github.com/TooLife/icost-app-mcp-server
- **问题反馈**: https://github.com/TooLife/icost-app-mcp-server/issues
- **FastMCP 框架**: https://github.com/jlowin/fastmcp
- **MCP 协议规范**: https://modelcontextprotocol.io/

## 📞 支持

- 📧 邮箱: json.tang.dev@gmail.com
- 🐛 问题: [GitHub Issues](https://github.com/TooLife/icost-app-mcp-server/issues)

## 🙏 致谢

- 感谢 [FastMCP](https://github.com/jlowin/fastmcp) 框架提供的强大基础
- 感谢 iCost 应用团队的 URL Scheme 支持
- 基于现代 Python 开发最佳实践构建
- 该项目不设计商用，仅用于个人学习和个人使用
