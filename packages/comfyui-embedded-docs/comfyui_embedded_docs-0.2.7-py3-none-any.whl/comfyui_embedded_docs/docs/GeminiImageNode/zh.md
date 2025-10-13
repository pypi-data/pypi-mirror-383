> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/GeminiImageNode/zh.md)

GeminiImage 节点通过谷歌的 Gemini AI 模型生成文本和图像响应。它允许您提供包括文本提示、图像和文件在内的多模态输入，以创建连贯的文本和图像输出。该节点负责与最新 Gemini 模型的所有 API 通信和响应解析。

## 输入参数

| 参数 | 数据类型 | 输入类型 | 默认值 | 取值范围 | 描述 |
|------|-----------|------------|---------|-------|-------------|
| `prompt` | STRING | 必填 | "" | - | 用于生成的文本提示 |
| `model` | COMBO | 必填 | gemini_2_5_flash_image_preview | 可用的 Gemini 模型<br>选项从 GeminiImageModel 枚举中提取 | 用于生成响应的 Gemini 模型 |
| `seed` | INT | 必填 | 42 | 0 到 18446744073709551615 | 当种子固定为特定值时，模型会尽力为重复请求提供相同的响应。不保证确定性输出。此外，即使使用相同的种子值，更改模型或参数设置（如温度）也可能导致响应变化。默认使用随机种子值 |
| `images` | IMAGE | 可选 | 无 | - | 用作模型上下文的可选图像。要包含多个图像，可以使用 Batch Images 节点 |
| `files` | GEMINI_INPUT_FILES | 可选 | 无 | - | 用作模型上下文的可选文件。接受来自 Gemini Generate Content Input Files 节点的输入 |

*注意：该节点包含由系统自动处理的隐藏参数（`auth_token`、`comfy_api_key`、`unique_id`），无需用户输入。*

## 输出参数

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `IMAGE` | IMAGE | 从 Gemini 模型生成的图像响应 |
| `STRING` | STRING | 从 Gemini 模型生成的文本响应 |
