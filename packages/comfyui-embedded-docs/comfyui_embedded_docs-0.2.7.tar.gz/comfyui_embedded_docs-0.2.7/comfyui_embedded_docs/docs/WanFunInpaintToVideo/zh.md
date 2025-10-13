> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/WanFunInpaintToVideo/zh.md)

WanFunInpaintToVideo 节点通过在起始图像和结束图像之间进行修复来创建视频序列。它接收正向和负向条件提示以及可选的帧图像，以生成视频潜在表示。该节点支持可配置尺寸和长度参数来处理视频生成。

## 输入参数

| 参数 | 数据类型 | 必填 | 取值范围 | 描述 |
|-----------|-----------|----------|-------|-------------|
| `正向` | CONDITIONING | 是 | - | 用于视频生成的正向条件提示 |
| `负向` | CONDITIONING | 是 | - | 视频生成中需要避免的负向条件提示 |
| `vae` | VAE | 是 | - | 用于编码/解码操作的 VAE 模型 |
| `宽度` | INT | 是 | 16 至 MAX_RESOLUTION | 输出视频宽度（像素）（默认：832，步长：16） |
| `高度` | INT | 是 | 16 至 MAX_RESOLUTION | 输出视频高度（像素）（默认：480，步长：16） |
| `长度` | INT | 是 | 1 至 MAX_RESOLUTION | 视频序列的帧数（默认：81，步长：4） |
| `批量大小` | INT | 是 | 1 至 4096 | 单批次生成的视频数量（默认：1） |
| `clip_vision_output` | CLIP_VISION_OUTPUT | 否 | - | 用于附加条件提示的可选 CLIP 视觉输出 |
| `起始图像` | IMAGE | 否 | - | 用于视频生成的可选起始帧图像 |
| `结束图像` | IMAGE | 否 | - | 用于视频生成的可选结束帧图像 |

## 输出参数

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `负向` | CONDITIONING | 处理后的正向条件输出 |
| `latent` | CONDITIONING | 处理后的负向条件输出 |
| `latent` | LATENT | 生成的视频潜在表示 |
