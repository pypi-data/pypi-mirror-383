> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/LoadImageSetFromFolderNode/zh.md)

## 概述

LoadImageSetFromFolderNode 从指定文件夹目录加载多张图像用于训练目的。它能自动检测常见图像格式，并可选择在使用不同方法调整图像尺寸后，将图像作为批次返回。

## 输入

| 参数 | 数据类型 | 必填 | 取值范围 | 描述 |
|-----------|-----------|----------|-------|-------------|
| `folder` | STRING | 是 | 多种选项可用 | 要从中加载图像的文件夹。 |
| `resize_method` | STRING | 否 | "None"<br>"Stretch"<br>"Crop"<br>"Pad" | 用于调整图像尺寸的方法（默认值："None"）。 |

## 输出

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `IMAGE` | IMAGE | 作为单个张量加载的图像批次。 |
