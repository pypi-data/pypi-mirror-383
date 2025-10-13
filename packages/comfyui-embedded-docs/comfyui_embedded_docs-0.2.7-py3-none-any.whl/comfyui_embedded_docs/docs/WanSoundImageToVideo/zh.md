> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/WanSoundImageToVideo/zh.md)

WanSoundImageToVideo 节点能够从图像生成视频内容，并支持可选的音频条件输入。该节点通过结合正向与负向条件提示以及 VAE 模型来创建视频潜变量，并可整合参考图像、音频编码、控制视频和运动参考等多种元素来引导视频生成过程。

## 输入参数

| 参数名 | 数据类型 | 必填 | 取值范围 | 描述 |
|--------|-----------|------|----------|------|
| `positive` | CONDITIONING | 是 | - | 正向条件提示，指导生成视频中应出现的内容 |
| `negative` | CONDITIONING | 是 | - | 负向条件提示，指定生成视频中应避免的内容 |
| `vae` | VAE | 是 | - | 用于编码和解码视频潜变量表示的 VAE 模型 |
| `width` | INT | 是 | 16 至 MAX_RESOLUTION | 输出视频的宽度（像素），默认值：832，必须能被 16 整除 |
| `height` | INT | 是 | 16 至 MAX_RESOLUTION | 输出视频的高度（像素），默认值：480，必须能被 16 整除 |
| `length` | INT | 是 | 1 至 MAX_RESOLUTION | 生成视频的帧数，默认值：77，必须能被 4 整除 |
| `batch_size` | INT | 是 | 1 至 4096 | 同时生成的视频数量，默认值：1 |
| `audio_encoder_output` | AUDIOENCODEROUTPUT | 否 | - | 可选的音频编码，可根据声音特征影响视频生成 |
| `ref_image` | IMAGE | 否 | - | 可选的参考图像，为视频内容提供视觉指导 |
| `control_video` | IMAGE | 否 | - | 可选的控制视频，指导生成视频的运动和结构 |
| `ref_motion` | IMAGE | 否 | - | 可选的运动参考，为视频中的运动模式提供指导 |

## 输出参数

| 输出名称 | 数据类型 | 描述 |
|----------|-----------|------|
| `positive` | CONDITIONING | 经过处理的正向条件提示，已适配视频生成需求 |
| `negative` | CONDITIONING | 经过处理的负向条件提示，已适配视频生成需求 |
| `latent` | LATENT | 潜空间中的生成视频表示，可解码为最终视频帧 |
