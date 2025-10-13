> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/IdeogramV2/zh.md)

# Ideogram V2 节点

Ideogram V2 节点使用 Ideogram V2 AI 模型生成图像。它接收文本提示和多种生成设置，通过 API 服务创建图像。该节点支持不同的宽高比、分辨率和风格选项，以自定义输出图像。

## 输入参数

| 参数 | 数据类型 | 必需 | 取值范围 | 描述 |
|-----------|-----------|----------|-------|-------------|
| `prompt` | STRING | 是 | - | 图像生成的提示词（默认：空字符串） |
| `turbo` | BOOLEAN | 否 | - | 是否使用极速模式（生成速度更快，可能降低质量）（默认：False） |
| `aspect_ratio` | COMBO | 否 | "1:1"<br>"16:9"<br>"9:16"<br>"4:3"<br>"3:4"<br>"3:2"<br>"2:3" | 图像生成的宽高比。当分辨率未设置为 AUTO 时忽略此设置。（默认："1:1"） |
| `resolution` | COMBO | 否 | "Auto"<br>"1024x1024"<br>"1152x896"<br>"896x1152"<br>"1216x832"<br>"832x1216"<br>"1344x768"<br>"768x1344"<br>"1536x640"<br>"640x1536" | 图像生成的分辨率。如果未设置为 AUTO，将覆盖 aspect_ratio 设置。（默认："Auto"） |
| `magic_prompt_option` | COMBO | 否 | "AUTO"<br>"ON"<br>"OFF" | 确定生成过程中是否使用 MagicPrompt（默认："AUTO"） |
| `seed` | INT | 否 | 0-2147483647 | 生成随机种子（默认：0） |
| `style_type` | COMBO | 否 | "AUTO"<br>"GENERAL"<br>"REALISTIC"<br>"DESIGN"<br>"RENDER_3D"<br>"ANIME" | 生成风格类型（仅限 V2 版本）（默认："NONE"） |
| `negative_prompt` | STRING | 否 | - | 图像中需要排除的内容描述（默认：空字符串） |
| `num_images` | INT | 否 | 1-8 | 生成的图像数量（默认：1） |

**注意：** 当 `resolution` 未设置为 "Auto" 时，它将覆盖 `aspect_ratio` 设置。`num_images` 参数每次生成最多限制为 8 张图像。

## 输出结果

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `output` | IMAGE | 来自 Ideogram V2 模型生成的图像 |
