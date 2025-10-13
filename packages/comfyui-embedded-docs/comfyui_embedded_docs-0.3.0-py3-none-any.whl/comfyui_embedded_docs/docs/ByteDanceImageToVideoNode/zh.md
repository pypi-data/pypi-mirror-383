> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/ByteDanceImageToVideoNode/zh.md)

## 概述

ByteDance Image to Video 节点通过 API 使用字节跳动模型，基于输入图像和文本提示生成视频。该节点接收起始图像帧，并根据提供的描述创建视频序列。节点提供多种自定义选项，包括视频分辨率、宽高比、时长和其他生成参数。

## 输入

| 参数 | 数据类型 | 输入类型 | 默认值 | 范围 | 描述 |
|------|-----------|------------|---------|-------|-------------|
| `model` | STRING | COMBO | seedance_1_pro | Image2VideoModelName 选项 | 模型名称 |
| `prompt` | STRING | STRING | - | - | 用于生成视频的文本提示。 |
| `image` | IMAGE | IMAGE | - | - | 用作视频起始帧的图像。 |
| `resolution` | STRING | COMBO | - | ["480p", "720p", "1080p"] | 输出视频的分辨率。 |
| `aspect_ratio` | STRING | COMBO | - | ["adaptive", "16:9", "4:3", "1:1", "3:4", "9:16", "21:9"] | 输出视频的宽高比。 |
| `duration` | INT | INT | 5 | 3-12 | 输出视频的时长（单位：秒）。 |
| `seed` | INT | INT | 0 | 0-2147483647 | 生成视频时使用的随机种子。 |
| `camera_fixed` | BOOLEAN | BOOLEAN | False | - | 是否固定摄像机。平台会在您的提示词后附加固定摄像机的指令，但不保证实际效果。 |
| `watermark` | BOOLEAN | BOOLEAN | True | - | 是否在视频中添加“AI生成”水印。 |

## 输出

| 输出名称 | 数据类型 | 描述 |
|----------|-----------|-------------|
| `output` | VIDEO | 基于输入图像和提示参数生成的视频文件。 |
