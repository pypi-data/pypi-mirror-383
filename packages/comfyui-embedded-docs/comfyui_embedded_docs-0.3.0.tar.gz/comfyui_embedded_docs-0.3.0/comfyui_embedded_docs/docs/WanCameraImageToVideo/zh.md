> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/WanCameraImageToVideo/zh.md)

WanCameraImageToVideo 节点通过生成视频生成的潜在表示，将图像转换为视频序列。它处理条件输入和可选的起始图像，以创建可用于视频模型的视频潜在表示。该节点支持相机条件和 CLIP 视觉输出，以增强视频生成的控制。

## 输入参数

| 参数名 | 数据类型 | 必填 | 取值范围 | 描述 |
|-----------|-----------|----------|-------|-------------|
| `positive` | CONDITIONING | 是 | - | 用于视频生成的正向条件提示 |
| `negative` | CONDITIONING | 是 | - | 视频生成中需要避免的负向条件提示 |
| `vae` | VAE | 是 | - | 用于将图像编码到潜在空间的 VAE 模型 |
| `width` | INT | 是 | 16 至 MAX_RESOLUTION | 输出视频的宽度（像素）（默认：832，步长：16） |
| `height` | INT | 是 | 16 至 MAX_RESOLUTION | 输出视频的高度（像素）（默认：480，步长：16） |
| `length` | INT | 是 | 1 至 MAX_RESOLUTION | 视频序列中的帧数（默认：81，步长：4） |
| `batch_size` | INT | 是 | 1 至 4096 | 同时生成的视频数量（默认：1） |
| `clip_vision_output` | CLIP_VISION_OUTPUT | 否 | - | 可选的 CLIP 视觉输出，用于附加条件控制 |
| `start_image` | IMAGE | 否 | - | 可选的起始图像，用于初始化视频序列 |
| `camera_conditions` | WAN_CAMERA_EMBEDDING | 否 | - | 可选的相机嵌入条件，用于视频生成 |

**注意：** 当提供 `start_image` 时，节点会使用它来初始化视频序列，并应用遮罩将起始帧与生成的内容混合。`camera_conditions` 和 `clip_vision_output` 参数是可选的，但当提供时，它们会修改正向和负向提示的条件。

## 输出参数

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `positive` | CONDITIONING | 应用了相机条件和 CLIP 视觉输出的修改后正向条件 |
| `negative` | CONDITIONING | 应用了相机条件和 CLIP 视觉输出的修改后负向条件 |
| `latent` | LATENT | 生成的视频潜在表示，可用于视频模型 |
