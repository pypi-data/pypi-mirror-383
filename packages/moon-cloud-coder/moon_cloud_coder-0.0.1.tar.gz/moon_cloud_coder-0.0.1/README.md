# Moon-Cloud-Coder

AI-powered command line tool for developers using Qwen models

## 项目描述

Moon-Cloud-Coder 是一个基于阿里云通义千问（Qwen）模型的AI命令行工具，专为开发者设计。它可以帮助开发者完成代码分析、生成、调试等任务。

## 功能特性

- 交互式AI对话
- 代码分析和生成
- 支持多种认证方式（API Key、OAuth）
- 丰富的命令行选项
- 文件内容分析支持

## 安装

```bash
pip install moon-cloud-coder
```

## 使用方法

### 交互模式
```bash
moon-cloud-coder
```

### 非交互模式
```bash
moon-cloud-coder --prompt "你的问题或请求"
```

### 认证设置
```bash
# 使用命令行进行认证
moon-cloud-coder
# 然后在交互模式中输入 /auth 命令
```

## 认证方式

项目支持两种认证方式：
1. API Key - 通过 `DASHSCOPE_API_KEY` 环境变量
2. Qwen OAuth - 通过OAuth流程，享有免费额度

## 配置

可以创建 `MoonCloud.md` 文件来自定义AI交互指令。

## 开发

```bash
# 克隆项目
git clone <repository-url>

# 安装开发依赖
pip install -e ".[dev]"
```

## 许可证

MIT