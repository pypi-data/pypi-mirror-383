> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/Hunyuan3Dv2Conditioning/zh.md)

## 概述

Hunyuan3Dv2Conditioning 节点处理 CLIP 视觉输出，为视频模型生成条件数据。它从视觉输出中提取最后隐藏状态的嵌入表示，并创建正负条件对。正条件使用实际的嵌入表示，而负条件则使用相同形状的零值嵌入表示。

## 输入

| 参数 | 数据类型 | 必需 | 取值范围 | 描述 |
|-----------|-----------|----------|-------|-------------|
| `clip视觉输出` | CLIP_VISION_OUTPUT | 是 | - | 来自 CLIP 视觉模型的输出，包含视觉嵌入表示 |

## 输出

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `反向` | CONDITIONING | 包含 CLIP 视觉嵌入表示的正条件数据 |
| `negative` | CONDITIONING | 包含与正条件嵌入形状匹配的零值嵌入表示的负条件数据 |
