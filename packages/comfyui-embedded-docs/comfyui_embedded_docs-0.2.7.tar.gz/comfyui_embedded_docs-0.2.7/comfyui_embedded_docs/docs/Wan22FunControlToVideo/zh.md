> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/Wan22FunControlToVideo/zh.md)

Wan22FunControlToVideo 节点使用 Wan 视频模型架构为视频生成准备条件输入和潜在表示。该节点处理正向和负向条件输入，以及可选的参考图像和控制视频，以创建视频合成所需的潜在空间表示。该节点处理空间缩放和时间维度，为视频模型生成适当的条件数据。

## 输入参数

| 参数 | 数据类型 | 必需 | 范围 | 描述 |
|-----------|-----------|----------|-------|-------------|
| `positive` | CONDITIONING | 是 | - | 用于引导视频生成的正向条件输入 |
| `negative` | CONDITIONING | 是 | - | 用于引导视频生成的负向条件输入 |
| `vae` | VAE | 是 | - | 用于将图像编码到潜在空间的 VAE 模型 |
| `width` | INT | 否 | 16 到 MAX_RESOLUTION | 输出视频宽度（像素）（默认：832，步长：16） |
| `height` | INT | 否 | 16 到 MAX_RESOLUTION | 输出视频高度（像素）（默认：480，步长：16） |
| `length` | INT | 否 | 1 到 MAX_RESOLUTION | 视频序列中的帧数（默认：81，步长：4） |
| `batch_size` | INT | 否 | 1 到 4096 | 要生成的视频序列数量（默认：1） |
| `ref_image` | IMAGE | 否 | - | 用于提供视觉引导的可选参考图像 |
| `control_video` | IMAGE | 否 | - | 用于引导生成过程的可选控制视频 |

**注意：** `length` 参数按 4 帧的块进行处理，节点会自动处理潜在空间的时间缩放。当提供 `ref_image` 时，它会通过参考潜在表示影响条件输入。当提供 `control_video` 时，它会直接影响条件输入中使用的拼接潜在表示。

## 输出结果

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `positive` | CONDITIONING | 包含视频特定潜在数据的修改后正向条件输入 |
| `negative` | CONDITIONING | 包含视频特定潜在数据的修改后负向条件输入 |
| `latent` | LATENT | 具有适当视频生成维度的空潜在张量 |
