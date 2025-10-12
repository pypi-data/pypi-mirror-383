# 使用方法

## 命令行选项

```bash
moon-cloud-coder [OPTIONS]
```

### 选项

- `-p, --prompt TEXT`: 非交互式模式下的提示语
- `-m, --model TEXT`: 使用的模型名称 (默认: qwen3-coder-plus)

## 交互模式

运行以下命令进入交互模式：

```bash
moon-cloud-coder
```

在交互模式中，您可以：

- 输入问题或请求，AI将为您生成代码或提供帮助
- 使用 `@路径/文件` 来分析特定文件
- 使用命令如 `/help`, `/auth`, `/exit` 等

## 可用命令

- `/help` - 显示帮助信息
- `/auth` - 更改认证方式
- `/exit` - 退出程序
- `/docs` - 获取文档链接
- `/config` - 显示配置信息

## 认证

程序支持两种认证方式：

1. **Qwen OAuth** (推荐) - 享有免费额度
2. **API Key** - 通过 DASHSCOPE_API_KEY 环境变量

## 自定义指令

您可以通过创建 `MoonCloud.md` 文件来自定义AI交互指令。