> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/OpenAIChatNode/zh.md)

此节点通过 OpenAI 模型生成文本回复。它允许您通过发送文本提示并接收生成的回复来与 AI 模型进行对话。该节点支持多轮对话，能够记住先前的上下文，并且还可以处理图像和文件作为模型的附加上下文。

## 输入参数

| 参数名 | 数据类型 | 必填 | 取值范围 | 描述 |
|-----------|-----------|----------|-------|-------------|
| `prompt` | STRING | 是 | - | 模型的文本输入，用于生成回复（默认：空） |
| `persist_context` | BOOLEAN | 是 | - | 在多轮对话中保持聊天上下文（默认：True） |
| `model` | COMBO | 是 | 提供多种 OpenAI 模型 | 用于生成回复的 OpenAI 模型 |
| `images` | IMAGE | 否 | - | 用作模型上下文的可选图像。要包含多张图像，可以使用批处理图像节点（默认：None） |
| `files` | OPENAI_INPUT_FILES | 否 | - | 用作模型上下文的可选文件。接受来自 OpenAI 聊天输入文件节点的输入（默认：None） |
| `advanced_options` | OPENAI_CHAT_CONFIG | 否 | - | 模型的可选配置。接受来自 OpenAI 聊天高级选项节点的输入（默认：None） |

## 输出参数

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `output_text` | STRING | 由 OpenAI 模型生成的文本回复 |
