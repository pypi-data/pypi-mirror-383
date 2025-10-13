> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/ByteDanceImageReferenceNode/zh.md)

字节跳动图像参考节点使用文本提示和一到四张参考图像来生成视频。它将图像和提示发送到外部 API 服务，该服务会根据您的描述创建视频，同时融入参考图像的视觉风格和内容。该节点提供了视频分辨率、宽高比、时长和其他生成参数的各种控制选项。

## 输入参数

| 参数名 | 数据类型 | 输入类型 | 默认值 | 取值范围 | 描述 |
|-----------|-----------|------------|---------|-------|-------------|
| `model` | MODEL | COMBO | seedance_1_lite | seedance_1_lite | 模型名称 |
| `prompt` | STRING | STRING | - | - | 用于生成视频的文本提示。 |
| `images` | IMAGE | IMAGE | - | - | 一到四张图像。 |
| `resolution` | STRING | COMBO | - | 480p, 720p | 输出视频的分辨率。 |
| `aspect_ratio` | STRING | COMBO | - | adaptive, 16:9, 4:3, 1:1, 3:4, 9:16, 21:9 | 输出视频的宽高比。 |
| `duration` | INT | INT | 5 | 3-12 | 输出视频的时长（单位：秒）。 |
| `seed` | INT | INT | 0 | 0-2147483647 | 用于生成的随机种子。 |
| `watermark` | BOOLEAN | BOOLEAN | True | - | 是否在视频上添加"AI生成"水印。 |

## 输出参数

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `output` | VIDEO | 基于输入提示和参考图像生成的视频文件。 |
