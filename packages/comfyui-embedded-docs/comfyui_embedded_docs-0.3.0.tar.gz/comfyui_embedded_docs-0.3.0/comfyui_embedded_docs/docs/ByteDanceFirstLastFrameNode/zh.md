> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/ByteDanceFirstLastFrameNode/zh.md)

该节点通过文本提示词结合首尾帧图像生成视频。它根据您的描述和两个关键帧创建完整的视频序列，实现帧与帧之间的过渡。该节点提供多种选项来控制视频的分辨率、宽高比、时长及其他生成参数。

## 输入参数

| 参数名 | 数据类型 | 输入类型 | 默认值 | 取值范围 | 描述 |
|--------|-----------|------------|---------|-------|-------------|
| `model` | COMBO | 下拉选项 | seedance_1_lite | seedance_1_lite | 模型名称 |
| `prompt` | STRING | 字符串 | - | - | 用于生成视频的文本提示词 |
| `first_frame` | IMAGE | 图像 | - | - | 视频使用的首帧图像 |
| `last_frame` | IMAGE | 图像 | - | - | 视频使用的尾帧图像 |
| `resolution` | COMBO | 下拉选项 | - | 480p, 720p, 1080p | 输出视频的分辨率 |
| `aspect_ratio` | COMBO | 下拉选项 | - | adaptive, 16:9, 4:3, 1:1, 3:4, 9:16, 21:9 | 输出视频的宽高比 |
| `duration` | INT | 滑块 | 5 | 3-12 | 输出视频的时长（单位：秒） |
| `seed` | INT | 数值 | 0 | 0-2147483647 | 生成时使用的随机种子（可选） |
| `camera_fixed` | BOOLEAN | 布尔值 | False | - | 指定是否固定摄像机。平台会在提示词后附加固定摄像机的指令，但不保证实际效果（可选） |
| `watermark` | BOOLEAN | 布尔值 | True | - | 是否为视频添加"AI生成"水印（可选） |

## 输出参数

| 输出名称 | 数据类型 | 描述 |
|----------|-----------|-------------|
| `output` | VIDEO | 生成的视频文件 |
