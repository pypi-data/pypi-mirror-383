> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/OpenAIInputFiles/zh.md)

> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！[在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/OpenAIInputFiles/en.md)

加载并格式化用于 OpenAI API 的输入文件。此节点准备文本和 PDF 文件，作为上下文输入提供给 OpenAI 聊天节点。生成响应时，OpenAI 模型将读取这些文件。可以将多个输入文件节点链接在一起，以便在单条消息中包含多个文件。

## 输入参数

| 参数 | 数据类型 | 必填 | 取值范围 | 描述 |
|-----------|-----------|----------|-------|-------------|
| `file` | COMBO | 是 | 提供多个选项 | 作为模型上下文输入的文件。目前仅接受文本文件 (.txt) 和 PDF 文件 (.pdf)。文件必须小于 32MB。 |
| `OPENAI_INPUT_FILES` | OPENAI_INPUT_FILES | 否 | 不适用 | 可选的附加文件，用于与此节点加载的文件批量处理。允许链接输入文件，以便单条消息可以包含多个输入文件。 |

**文件限制：**

- 仅支持 .txt 和 .pdf 文件
- 最大文件大小：32MB
- 文件从输入目录加载

## 输出参数

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `OPENAI_INPUT_FILES` | OPENAI_INPUT_FILES | 格式化后的输入文件，已准备好用作 OpenAI API 调用的上下文。 |
