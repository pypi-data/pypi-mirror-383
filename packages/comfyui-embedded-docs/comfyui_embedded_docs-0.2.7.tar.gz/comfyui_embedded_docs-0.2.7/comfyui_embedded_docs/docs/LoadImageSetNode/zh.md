> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/LoadImageSetNode/zh.md)

## 概述

LoadImageSetNode 从输入目录加载多张图像，用于批处理和训练目的。它支持多种图像格式，并可选使用不同方法调整图像尺寸。该节点将所有选中的图像作为批次处理，并以单个张量形式返回。

## 输入

| 参数 | 数据类型 | 必需 | 取值范围 | 描述 |
|-----------|-----------|----------|-------|-------------|
| `images` | IMAGE | 是 | 多个图像文件 | 从输入目录选择多张图像。支持 PNG、JPG、JPEG、WEBP、BMP、GIF、JPE、APNG、TIF 和 TIFF 格式。允许批量选择图像。 |
| `resize_method` | STRING | 否 | "None"<br>"Stretch"<br>"Crop"<br>"Pad" | 调整加载图像尺寸的可选方法（默认："None"）。选择 "None" 保持原始尺寸，"Stretch" 强制调整尺寸，"Crop" 通过裁剪保持宽高比，或 "Pad" 通过添加填充保持宽高比。 |

## 输出

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `IMAGE` | IMAGE | 包含所有加载图像作为批次的张量，用于进一步处理。 |
