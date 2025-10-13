> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/WanTrackToVideo/zh.md)

WanTrackToVideo 节点通过处理轨迹点并生成相应的视频帧，将运动跟踪数据转换为视频序列。它接收跟踪坐标作为输入，并生成可用于视频生成的视频条件信息和潜在表示。当未提供轨迹数据时，该节点将回退到标准的图像到视频转换模式。

## 输入参数

| 参数名 | 数据类型 | 必填 | 取值范围 | 描述 |
|-----------|-----------|----------|-------|-------------|
| `positive` | CONDITIONING | 是 | - | 用于视频生成的正向条件信息 |
| `negative` | CONDITIONING | 是 | - | 用于视频生成的负向条件信息 |
| `vae` | VAE | 是 | - | 用于编码和解码的 VAE 模型 |
| `tracks` | STRING | 是 | - | JSON 格式的跟踪数据，作为多行字符串（默认："[]"） |
| `width` | INT | 是 | 16 至 MAX_RESOLUTION | 输出视频的宽度，单位为像素（默认：832，步长：16） |
| `height` | INT | 是 | 16 至 MAX_RESOLUTION | 输出视频的高度，单位为像素（默认：480，步长：16） |
| `length` | INT | 是 | 1 至 MAX_RESOLUTION | 输出视频的帧数（默认：81，步长：4） |
| `batch_size` | INT | 是 | 1 至 4096 | 同时生成的视频数量（默认：1） |
| `temperature` | FLOAT | 是 | 1.0 至 1000.0 | 运动修补的温度参数（默认：220.0，步长：0.1） |
| `topk` | INT | 是 | 1 至 10 | 运动修补的 top-k 值（默认：2） |
| `start_image` | IMAGE | 否 | - | 用于视频生成的起始图像 |
| `clip_vision_output` | CLIPVISIONOUTPUT | 否 | - | 用于附加条件信息的 CLIP 视觉输出 |

**注意：** 当 `tracks` 包含有效的跟踪数据时，节点会处理运动轨迹以生成视频。当 `tracks` 为空时，节点将切换到标准的图像到视频模式。如果提供了 `start_image`，它将初始化视频序列的第一帧。

## 输出参数

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `positive` | CONDITIONING | 应用了运动轨迹信息的正向条件信息 |
| `negative` | CONDITIONING | 应用了运动轨迹信息的负向条件信息 |
| `latent` | LATENT | 生成的视频潜在表示 |
