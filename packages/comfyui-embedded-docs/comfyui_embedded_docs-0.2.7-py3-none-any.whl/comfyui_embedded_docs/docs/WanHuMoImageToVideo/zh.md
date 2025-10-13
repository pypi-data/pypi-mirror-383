> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/WanHuMoImageToVideo/zh.md)

WanHuMoImageToVideo 节点通过生成视频帧的潜在表示，将图像转换为视频序列。该节点处理条件输入，并可结合参考图像和音频嵌入来影响视频生成。节点输出适用于视频合成的修改后条件数据和潜在表示。

## 输入参数

| 参数名 | 数据类型 | 必填 | 取值范围 | 描述 |
|-----------|-----------|----------|-------|-------------|
| `positive` | CONDITIONING | 是 | - | 正向条件输入，引导视频生成朝向期望内容 |
| `negative` | CONDITIONING | 是 | - | 负向条件输入，使视频生成远离不需要的内容 |
| `vae` | VAE | 是 | - | 用于将参考图像编码到潜在空间的 VAE 模型 |
| `width` | INT | 是 | 16 至 MAX_RESOLUTION | 输出视频帧的宽度（单位：像素），默认值：832，必须能被 16 整除 |
| `height` | INT | 是 | 16 至 MAX_RESOLUTION | 输出视频帧的高度（单位：像素），默认值：480，必须能被 16 整除 |
| `length` | INT | 是 | 1 至 MAX_RESOLUTION | 生成视频序列的帧数，默认值：97 |
| `batch_size` | INT | 是 | 1 至 4096 | 同时生成的视频序列数量，默认值：1 |
| `audio_encoder_output` | AUDIOENCODEROUTPUT | 否 | - | 可选的音频编码数据，可根据音频内容影响视频生成 |
| `ref_image` | IMAGE | 否 | - | 可选的参考图像，用于指导视频生成的风格和内容 |

**注意：** 当提供参考图像时，它会被编码并添加到正向和负向条件中。当提供音频编码器输出时，它会被处理并合并到条件数据中。

## 输出结果

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `positive` | CONDITIONING | 修改后的正向条件，包含参考图像和/或音频嵌入 |
| `negative` | CONDITIONING | 修改后的负向条件，包含参考图像和/或音频嵌入 |
| `latent` | LATENT | 生成的潜在表示，包含视频序列数据 |
