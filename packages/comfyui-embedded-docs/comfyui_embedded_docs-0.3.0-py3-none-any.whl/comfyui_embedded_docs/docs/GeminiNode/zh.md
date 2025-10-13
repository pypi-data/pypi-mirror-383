> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/GeminiNode/zh.md)

此节点允许用户与 Google 的 Gemini AI 模型交互以生成文本响应。您可以提供多种类型的输入，包括文本、图像、音频、视频和文件，作为模型的上下文，以生成更相关和更有意义的响应。该节点会自动处理所有 API 通信和响应解析。

## 输入参数

| 参数 | 数据类型 | 必需 | 取值范围 | 描述 |
|-----------|-----------|----------|-------|-------------|
| `prompt` | STRING | 是 | - | 提供给模型的文本输入，用于生成响应。您可以包含详细的指令、问题或上下文信息。默认值：空字符串。 |
| `model` | COMBO | 是 | `gemini-2.0-flash-exp`<br>`gemini-2.0-flash-thinking-exp`<br>`gemini-2.5-pro-exp`<br>`gemini-2.0-flash`<br>`gemini-2.0-flash-thinking`<br>`gemini-2.5-pro`<br>`gemini-2.0-flash-lite`<br>`gemini-1.5-flash`<br>`gemini-1.5-flash-8b`<br>`gemini-1.5-pro`<br>`gemini-1.0-pro` | 用于生成响应的 Gemini 模型。默认值：gemini-2.5-pro。 |
| `seed` | INT | 是 | 0 到 18446744073709551615 | 当种子固定为特定值时，模型会尽力为重复的请求提供相同的响应。不保证输出是确定性的。此外，即使使用相同的种子值，更改模型或参数设置（例如温度）也可能导致响应发生变化。默认情况下，使用随机种子值。默认值：42。 |
| `images` | IMAGE | 否 | - | 用作模型上下文的可选图像。要包含多个图像，您可以使用批处理图像节点。默认值：无。 |
| `audio` | AUDIO | 否 | - | 用作模型上下文的可选音频。默认值：无。 |
| `video` | VIDEO | 否 | - | 用作模型上下文的可选视频。默认值：无。 |
| `files` | GEMINI_INPUT_FILES | 否 | - | 用作模型上下文的可选文件。接受来自 Gemini 生成内容输入文件节点的输入。默认值：无。 |

## 输出结果

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `STRING` | STRING | 由 Gemini 模型生成的文本响应。 |
