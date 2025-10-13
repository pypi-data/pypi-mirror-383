> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/IdeogramV1/zh.md)

> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！[在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/IdeogramV1/en.md)

IdeogramV1 节点通过 API 使用 Ideogram V1 模型生成图像。它接收文本提示词和各种生成设置，根据您的输入创建一个或多个图像。该节点支持不同的宽高比和生成模式以自定义输出。

## 输入参数

| 参数 | 数据类型 | 必填 | 取值范围 | 描述 |
|-----------|-----------|----------|-------|-------------|
| `prompt` | STRING | 是 | - | 图像生成的提示词（默认：空） |
| `turbo` | BOOLEAN | 是 | - | 是否使用极速模式（生成速度更快，可能降低质量）（默认：False） |
| `aspect_ratio` | COMBO | 否 | "1:1"<br>"16:9"<br>"9:16"<br>"4:3"<br>"3:4"<br>"3:2"<br>"2:3" | 图像生成的宽高比（默认："1:1"） |
| `magic_prompt_option` | COMBO | 否 | "AUTO"<br>"ON"<br>"OFF" | 确定是否在生成中使用 MagicPrompt（默认："AUTO"） |
| `seed` | INT | 否 | 0-2147483647 | 生成使用的随机种子值（默认：0） |
| `negative_prompt` | STRING | 否 | - | 要从图像中排除的内容描述（默认：空） |
| `num_images` | INT | 否 | 1-8 | 要生成的图像数量（默认：1） |

**注意：** `num_images` 参数每次生成请求最多限制为 8 张图像。

## 输出参数

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `output` | IMAGE | 来自 Ideogram V1 模型生成的图像 |
