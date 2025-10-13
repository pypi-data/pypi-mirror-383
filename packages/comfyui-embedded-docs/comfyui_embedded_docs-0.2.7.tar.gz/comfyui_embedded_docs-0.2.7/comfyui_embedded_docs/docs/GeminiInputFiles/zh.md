> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/GeminiInputFiles/zh.md)

为 Gemini API 加载并格式化输入文件。此节点允许用户将文本文件 (.txt) 和 PDF 文件 (.pdf) 作为输入上下文包含在 Gemini 模型中。文件会被转换为 API 所需的适当格式，并且可以链接在一起，以便在单个请求中包含多个文件。

## 输入参数

| 参数 | 数据类型 | 必需 | 取值范围 | 描述 |
|-----------|-----------|----------|-------|-------------|
| `file` | COMBO | 是 | 提供多个选项 | 要作为模型上下文包含的输入文件。目前仅接受文本文件 (.txt) 和 PDF 文件 (.pdf)。文件必须小于最大输入文件大小限制。 |
| `GEMINI_INPUT_FILES` | GEMINI_INPUT_FILES | 否 | 不适用 | 一个可选的附加文件，用于与此节点加载的文件批量组合。允许链接输入文件，以便单个消息可以包含多个输入文件。 |

**注意：** `file` 参数仅显示小于最大输入文件大小限制的文本文件 (.txt) 和 PDF 文件 (.pdf)。文件会自动按名称过滤和排序。

## 输出

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `GEMINI_INPUT_FILES` | GEMINI_INPUT_FILES | 格式化后的文件数据，已准备好供 Gemini LLM 节点使用，包含已加载文件内容，格式符合 API 要求。 |
