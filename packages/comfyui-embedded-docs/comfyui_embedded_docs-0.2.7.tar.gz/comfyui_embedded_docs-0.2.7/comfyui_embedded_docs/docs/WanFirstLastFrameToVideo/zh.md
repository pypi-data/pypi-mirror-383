> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/WanFirstLastFrameToVideo/zh.md)

WanFirstLastFrameToVideo 节点通过结合起始帧和结束帧与文本提示来创建视频条件。它通过对首尾帧进行编码、应用遮罩指导生成过程，并在可用时整合 CLIP 视觉特征，为视频生成生成潜在表示。该节点为视频模型准备正向和负向条件，以在指定的起始点和结束点之间生成连贯序列。

## 输入参数

| 参数名 | 数据类型 | 必填 | 取值范围 | 描述 |
|--------|-----------|------|----------|------|
| `正向` | CONDITIONING | 是 | - | 用于指导视频生成的正向文本条件 |
| `负向` | CONDITIONING | 是 | - | 用于指导视频生成的负向文本条件 |
| `vae` | VAE | 是 | - | 用于将图像编码到潜在空间的 VAE 模型 |
| `宽度` | INT | 否 | 16 至 MAX_RESOLUTION | 输出视频宽度（默认：832，步长：16） |
| `高度` | INT | 否 | 16 至 MAX_RESOLUTION | 输出视频高度（默认：480，步长：16） |
| `长度` | INT | 否 | 1 至 MAX_RESOLUTION | 视频序列中的帧数（默认：81，步长：4） |
| `批量大小` | INT | 否 | 1 至 4096 | 同时生成的视频数量（默认：1） |
| `clip 视觉起始图像` | CLIP_VISION_OUTPUT | 否 | - | 从起始图像提取的 CLIP 视觉特征 |
| `clip 视觉结束图像` | CLIP_VISION_OUTPUT | 否 | - | 从结束图像提取的 CLIP 视觉特征 |
| `起始图像` | IMAGE | 否 | - | 视频序列的起始帧图像 |
| `结束图像` | IMAGE | 否 | - | 视频序列的结束帧图像 |

**注意：** 当同时提供 `start_image` 和 `end_image` 时，节点会创建在这两个帧之间过渡的视频序列。`clip_vision_start_image` 和 `clip_vision_end_image` 参数是可选的，但若提供，它们的 CLIP 视觉特征将被拼接并应用于正向和负向条件。

## 输出结果

| 输出名称 | 数据类型 | 描述 |
|----------|-----------|------|
| `负向` | CONDITIONING | 应用了视频帧编码和 CLIP 视觉特征的正向条件 |
| `latent` | CONDITIONING | 应用了视频帧编码和 CLIP 视觉特征的负向条件 |
| `latent` | LATENT | 空潜在张量，其维度与指定的视频参数匹配 |
