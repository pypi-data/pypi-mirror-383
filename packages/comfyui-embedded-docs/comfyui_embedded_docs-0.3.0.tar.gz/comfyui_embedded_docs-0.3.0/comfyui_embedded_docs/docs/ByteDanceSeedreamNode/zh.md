> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/ByteDanceSeedreamNode/zh.md)

字节跳动 Seedream 4 节点提供统一的文生图功能和高达 4K 分辨率的精准单句编辑能力。它可以根据文本提示创建新图像，或使用文本指令编辑现有图像。该节点支持单张图像生成和连续生成多张相关图像。

## 输入参数

| 参数名 | 数据类型 | 输入类型 | 默认值 | 取值范围 | 描述 |
|-----------|-----------|------------|---------|-------|-------------|
| `model` | MODEL | COMBO | "seedream-4-0-250828" | ["seedream-4-0-250828"] | 模型名称 |
| `prompt` | STRING | STRING | "" | - | 用于创建或编辑图像的文本提示 |
| `image` | IMAGE | IMAGE | - | - | 用于图生图的输入图像。单参考或多参考生成时，可输入1-10张图像列表 |
| `size_preset` | STRING | COMBO | RECOMMENDED_PRESETS_SEEDREAM_4 的第一个预设 | RECOMMENDED_PRESETS_SEEDREAM_4 的所有标签 | 选择推荐尺寸。选择"自定义"可使用下方的宽度和高度 |
| `width` | INT | INT | 2048 | 1024-4096 (步长64) | 图像的自定义宽度。仅当 `size_preset` 设置为 `Custom` 时生效 |
| `height` | INT | INT | 2048 | 1024-4096 (步长64) | 图像的自定义高度。仅当 `size_preset` 设置为 `Custom` 时生效 |
| `sequential_image_generation` | STRING | COMBO | "disabled" | ["disabled", "auto"] | 分组图像生成模式。"disabled"生成单张图像。"auto"让模型决定是否生成多张相关图像（如故事场景、角色变体） |
| `max_images` | INT | INT | 1 | 1-15 | 当 sequential_image_generation='auto' 时生成的最大图像数量。总图像数（输入+生成）不能超过15张 |
| `seed` | INT | INT | 0 | 0-2147483647 | 用于生成的随机种子 |
| `watermark` | BOOLEAN | BOOLEAN | True | - | 是否在图像上添加"AI生成"水印 |
| `fail_on_partial` | BOOLEAN | BOOLEAN | True | - | 如果启用，当任何请求的图像缺失或返回错误时将中止执行 |

## 输出参数

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `IMAGE` | IMAGE | 基于输入参数和提示生成的图像 |
