> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/ByteDanceImageNode/zh.md)

## 概述

ByteDance Image 节点通过基于文本提示的 API 使用字节跳动模型生成图像。它允许您选择不同的模型，指定图像尺寸，并控制各种生成参数，如种子值和引导尺度。该节点连接到字节跳动的图像生成服务并返回创建的图像。

## 输入

| 参数 | 数据类型 | 输入类型 | 默认值 | 范围 | 描述 |
|-----------|-----------|------------|---------|-------|-------------|
| `model` | MODEL | COMBO | seedream_3 | Text2ImageModelName 选项 | 模型名称 |
| `prompt` | STRING | STRING | - | - | 用于生成图像的文本提示 |
| `size_preset` | STRING | COMBO | - | RECOMMENDED_PRESETS 标签 | 选择推荐尺寸。选择 Custom 以使用下方的宽度和高度 |
| `width` | INT | INT | 1024 | 512-2048（步长 64） | 图像的自定义宽度。仅当 `size_preset` 设置为 `Custom` 时生效 |
| `height` | INT | INT | 1024 | 512-2048（步长 64） | 图像的自定义高度。仅当 `size_preset` 设置为 `Custom` 时生效 |
| `seed` | INT | INT | 0 | 0-2147483647（步长 1） | 用于生成的种子值（可选） |
| `guidance_scale` | FLOAT | FLOAT | 2.5 | 1.0-10.0（步长 0.01） | 值越高，图像越紧密遵循提示（可选） |
| `watermark` | BOOLEAN | BOOLEAN | True | - | 是否在图像上添加"AI 生成"水印（可选） |

## 输出

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `IMAGE` | IMAGE | 从字节跳动 API 生成的图像 |
