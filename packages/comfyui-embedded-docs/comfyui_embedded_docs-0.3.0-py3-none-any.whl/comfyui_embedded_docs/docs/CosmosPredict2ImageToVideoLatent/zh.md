> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/CosmosPredict2ImageToVideoLatent/zh.md)

CosmosPredict2ImageToVideoLatent 节点可从图像创建视频潜在表示以用于视频生成。它能够生成空白视频潜在表示，或结合起始和结束图像来创建具有指定尺寸和时长的视频序列。该节点负责将图像编码为适用于视频处理的潜在空间格式。

## 输入参数

| 参数 | 数据类型 | 必需 | 取值范围 | 描述 |
|------|-----------|------|----------|------|
| `vae` | VAE | 是 | - | 用于将图像编码到潜在空间的 VAE 模型 |
| `width` | INT | 否 | 16 至 MAX_RESOLUTION | 输出视频的宽度（单位：像素，默认值：848，必须能被 16 整除） |
| `height` | INT | 否 | 16 至 MAX_RESOLUTION | 输出视频的高度（单位：像素，默认值：480，必须能被 16 整除） |
| `length` | INT | 否 | 1 至 MAX_RESOLUTION | 视频序列的帧数（默认值：93，步长：4） |
| `batch_size` | INT | 否 | 1 至 4096 | 要生成的视频序列数量（默认值：1） |
| `start_image` | IMAGE | 否 | - | 视频序列的可选起始图像 |
| `end_image` | IMAGE | 否 | - | 视频序列的可选结束图像 |

**注意：** 当未提供 `start_image` 和 `end_image` 时，节点将生成空白视频潜在表示。当提供图像时，它们会被编码并放置在视频序列的起始和/或结束位置，并应用相应的遮罩。

## 输出结果

| 输出名称 | 数据类型 | 描述 |
|----------|-----------|------|
| `samples` | LATENT | 生成的视频潜在表示，包含编码后的视频序列 |
| `noise_mask` | LATENT | 指示在生成过程中应保留潜在表示哪些部分的遮罩 |
