> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/MinimaxHailuoVideoNode/zh.md)

## 概述

使用 MiniMax Hailuo-02 模型从文本提示生成视频。您可以选择提供起始图像作为第一帧，以创建从该图像继续的视频。

## 输入

| 参数 | 数据类型 | 必需 | 范围 | 描述 |
|-----------|-----------|----------|-------|-------------|
| `prompt_text` | STRING | 是 | - | 用于指导视频生成的文本提示。 |
| `seed` | INT | 否 | 0 到 18446744073709551615 | 用于创建噪声的随机种子（默认值：0）。 |
| `first_frame_image` | IMAGE | 否 | - | 可选图像，用作生成视频的第一帧。 |
| `prompt_optimizer` | BOOLEAN | 否 | - | 在需要时优化提示以提高生成质量（默认值：True）。 |
| `duration` | COMBO | 否 | `6`<br>`10` | 输出视频的长度，单位为秒（默认值：6）。 |
| `resolution` | COMBO | 否 | `"768P"`<br>`"1080P"` | 视频显示的尺寸。1080p 为 1920x1080，768p 为 1366x768（默认值："768P"）。 |

**注意：** 当使用 MiniMax-Hailuo-02 模型并选择 1080P 分辨率时，视频时长限制为 6 秒。

## 输出

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `output` | VIDEO | 生成的视频文件。 |
