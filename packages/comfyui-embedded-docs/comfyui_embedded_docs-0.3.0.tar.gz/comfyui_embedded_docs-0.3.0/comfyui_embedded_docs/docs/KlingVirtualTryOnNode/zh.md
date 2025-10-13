> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/KlingVirtualTryOnNode/zh.md)

# ## 概述

Kling 虚拟试穿节点。输入人物图像和服装图像，在人物身上试穿服装。您可以将多个服装物品图片合并为一张白色背景的图像。

# ## 输入

| 参数 | 数据类型 | 必需 | 范围 | 描述 |
|-----------|-----------|----------|-------|-------------|
| `human_image` | IMAGE | 是 | - | 用于试穿服装的人物图像 |
| `cloth_image` | IMAGE | 是 | - | 要在人物身上试穿的服装图像 |
| `model_name` | STRING | 是 | `"kolors-virtual-try-on-v1"` | 使用的虚拟试穿模型（默认："kolors-virtual-try-on-v1"） |

# ## 输出

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `output` | IMAGE | 生成的显示人物试穿服装后的图像 |
