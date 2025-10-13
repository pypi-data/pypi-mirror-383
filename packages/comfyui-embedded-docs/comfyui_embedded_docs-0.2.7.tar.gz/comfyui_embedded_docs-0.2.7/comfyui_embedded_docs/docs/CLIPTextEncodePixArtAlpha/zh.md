> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/CLIPTextEncodePixArtAlpha/zh.md)

## 概述

对文本进行编码并为 PixArt Alpha 设置分辨率条件。此节点处理文本输入并添加宽度和高度信息，以创建专门用于 PixArt Alpha 模型的条件数据。它不适用于 PixArt Sigma 模型。

## 输入

| 参数 | 数据类型 | 输入类型 | 默认值 | 范围 | 描述 |
|-----------|-----------|------------|---------|-------|-------------|
| `宽度` | INT | 输入 | 1024 | 0 到 MAX_RESOLUTION | 用于分辨率条件的宽度维度 |
| `高度` | INT | 输入 | 1024 | 0 到 MAX_RESOLUTION | 用于分辨率条件的高度维度 |
| `文本` | STRING | 输入 | - | - | 要编码的文本输入，支持多行输入和动态提示 |
| `剪辑` | CLIP | 输入 | - | - | 用于标记化和编码的 CLIP 模型 |

## 输出

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `CONDITIONING` | CONDITIONING | 包含文本标记和分辨率信息的编码条件数据 |
