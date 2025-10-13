> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/IdeogramV3/zh.md)

# Ideogram V3 节点

Ideogram V3 节点使用 Ideogram V3 模型生成图像。它支持基于文本提示的常规图像生成，以及在提供图像和遮罩时的图像编辑功能。该节点提供多种控制选项，包括宽高比、分辨率、生成速度以及可选的字符参考图像。

## 输入参数

| 参数 | 数据类型 | 必填 | 取值范围 | 描述 |
|-------|-----------|----------|-------|-------------|
| `prompt` | STRING | 是 | - | 用于图像生成或编辑的提示词（默认：空） |
| `image` | IMAGE | 否 | - | 用于图像编辑的可选参考图像 |
| `mask` | MASK | 否 | - | 用于局部重绘的可选遮罩（白色区域将被替换） |
| `aspect_ratio` | COMBO | 否 | "1:1"<br>"16:9"<br>"9:16"<br>"4:3"<br>"3:4"<br>"3:2"<br>"2:3" | 图像生成的宽高比。如果分辨率未设置为自动，则忽略此参数（默认："1:1"） |
| `resolution` | COMBO | 否 | "Auto"<br>"1024x1024"<br>"1152x896"<br>"896x1152"<br>"1216x832"<br>"832x1216"<br>"1344x768"<br>"768x1344"<br>"1536x640"<br>"640x1536" | 图像生成的分辨率。如果未设置为自动，将覆盖 aspect_ratio 设置（默认："Auto"） |
| `magic_prompt_option` | COMBO | 否 | "AUTO"<br>"ON"<br>"OFF" | 确定生成过程中是否使用 MagicPrompt（默认："AUTO"） |
| `seed` | INT | 否 | 0-2147483647 | 生成图像的随机种子（默认：0） |
| `num_images` | INT | 否 | 1-8 | 要生成的图像数量（默认：1） |
| `rendering_speed` | COMBO | 否 | "DEFAULT"<br>"TURBO"<br>"QUALITY" | 控制生成速度与质量之间的权衡（默认："DEFAULT"） |
| `character_image` | IMAGE | 否 | - | 用作字符参考的图像 |
| `character_mask` | MASK | 否 | - | 字符参考图像的可选遮罩 |

**参数约束：**

- 当同时提供 `image` 和 `mask` 时，节点将切换到编辑模式
- 如果只提供 `image` 或 `mask` 中的一个，将发生错误
- `character_mask` 需要与 `character_image` 同时存在
- 当 `resolution` 未设置为 "Auto" 时，`aspect_ratio` 参数将被忽略
- 局部重绘过程中，遮罩中的白色区域将被替换
- 字符遮罩和字符图像必须具有相同尺寸

## 输出结果

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `output` | IMAGE | 生成或编辑后的图像 |
