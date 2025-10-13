> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/WanPhantomSubjectToVideo/zh.md)

WanPhantomSubjectToVideo 节点通过处理条件输入和可选的参考图像来生成视频内容。它创建用于视频生成的潜在表示，并在提供输入图像时能够融入视觉引导。该节点通过时间维度拼接为视频模型准备条件数据，并输出修改后的条件数据以及生成的潜在视频数据。

## 输入参数

| 参数 | 数据类型 | 必需 | 取值范围 | 描述 |
|-----------|-----------|----------|-------|-------------|
| `positive` | CONDITIONING | 是 | - | 用于引导视频生成的正向条件输入 |
| `negative` | CONDITIONING | 是 | - | 用于避免某些特征的负向条件输入 |
| `vae` | VAE | 是 | - | 用于在提供图像时进行编码的 VAE 模型 |
| `width` | INT | 否 | 16 到 MAX_RESOLUTION | 输出视频宽度（像素）（默认：832，必须能被 16 整除） |
| `height` | INT | 否 | 16 到 MAX_RESOLUTION | 输出视频高度（像素）（默认：480，必须能被 16 整除） |
| `length` | INT | 否 | 1 到 MAX_RESOLUTION | 生成视频的帧数（默认：81，必须能被 4 整除） |
| `batch_size` | INT | 否 | 1 到 4096 | 同时生成的视频数量（默认：1） |
| `images` | IMAGE | 否 | - | 用于时间维度条件处理的可选参考图像 |

**注意：** 当提供 `images` 时，它们会自动放大以匹配指定的 `width` 和 `height`，并且仅使用前 `length` 帧进行处理。

## 输出结果

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `positive` | CONDITIONING | 修改后的正向条件数据，在提供图像时包含时间维度拼接 |
| `negative_text` | CONDITIONING | 修改后的负向条件数据，在提供图像时包含时间维度拼接 |
| `negative_img_text` | CONDITIONING | 负向条件数据，在提供图像时时间维度拼接被置零 |
| `latent` | LATENT | 生成的潜在视频表示，具有指定的尺寸和长度 |
