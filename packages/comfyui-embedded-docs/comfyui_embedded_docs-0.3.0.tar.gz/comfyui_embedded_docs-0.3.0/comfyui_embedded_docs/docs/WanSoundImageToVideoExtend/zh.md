> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/WanSoundImageToVideoExtend/zh.md)

WanSoundImageToVideoExtend 节点通过整合音频条件处理和参考图像来扩展图像到视频的生成功能。该节点接收正向和负向条件提示、视频潜在数据以及可选的音频嵌入，以生成扩展的视频序列。节点会处理这些输入内容，创建与音频线索同步的连贯视频输出。

## 输入参数

| 参数名 | 数据类型 | 必填 | 取值范围 | 描述 |
|-----------|-----------|----------|-------|-------------|
| `positive` | CONDITIONING | 是 | - | 正向条件提示，指导视频应包含的内容 |
| `negative` | CONDITIONING | 是 | - | 负向条件提示，指定视频应避免的内容 |
| `vae` | VAE | 是 | - | 用于视频帧编码和解码的变分自编码器 |
| `length` | INT | 是 | 1 到 MAX_RESOLUTION | 为视频序列生成的帧数（默认值：77，步长：4） |
| `video_latent` | LATENT | 是 | - | 作为扩展起点的初始视频潜在表示 |
| `audio_encoder_output` | AUDIOENCODEROUTPUT | 否 | - | 可选的音频嵌入，可根据声音特征影响视频生成 |
| `ref_image` | IMAGE | 否 | - | 可选的参考图像，为视频生成提供视觉指导 |
| `control_video` | IMAGE | 否 | - | 可选的控制视频，可指导生成视频的运动和风格 |

## 输出参数

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `positive` | CONDITIONING | 应用了视频上下文的已处理正向条件提示 |
| `negative` | CONDITIONING | 应用了视频上下文的已处理负向条件提示 |
| `latent` | LATENT | 包含扩展视频序列的生成视频潜在表示 |
