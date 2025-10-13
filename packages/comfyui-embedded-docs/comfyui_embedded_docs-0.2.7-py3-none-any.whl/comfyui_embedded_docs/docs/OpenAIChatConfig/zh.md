> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/OpenAIChatConfig/zh.md)

OpenAIChatConfig 节点用于为 OpenAI Chat 节点设置额外的配置选项。它提供高级设置，用于控制模型生成响应的方式，包括截断行为、输出长度限制和自定义指令。

## 输入参数

| 参数 | 数据类型 | 必填 | 取值范围 | 描述 |
|------|-----------|----------|-------|-------------|
| `truncation` | COMBO | 是 | `"auto"`<br>`"disabled"` | 模型响应使用的截断策略。auto：如果本次响应及之前对话的上下文超出模型的上下文窗口大小，模型将通过丢弃对话中间部分的输入项来截断响应以适应上下文窗口。disabled：如果模型响应将超出模型的上下文窗口大小，请求将失败并返回 400 错误（默认值："auto"） |
| `max_output_tokens` | INT | 否 | 16-16384 | 响应生成的最大令牌数上限，包括可见的输出令牌（默认值：4096） |
| `instructions` | STRING | 否 | - | 模型响应的附加指令（支持多行输入） |

## 输出参数

| 输出名称 | 数据类型 | 描述 |
|----------|-----------|-------------|
| `OPENAI_CHAT_CONFIG` | OPENAI_CHAT_CONFIG | 包含指定设置的配置对象，用于 OpenAI Chat 节点 |
