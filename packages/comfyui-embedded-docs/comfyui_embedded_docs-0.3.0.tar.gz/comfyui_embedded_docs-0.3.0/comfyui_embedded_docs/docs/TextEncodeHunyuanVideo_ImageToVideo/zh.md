> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/TextEncodeHunyuanVideo_ImageToVideo/zh.md)

TextEncodeHunyuanVideo_ImageToVideo 节点通过将文本提示与图像嵌入相结合，为视频生成创建条件数据。它使用 CLIP 模型处理文本输入和来自 CLIP 视觉输出的视觉信息，然后根据指定的图像交错设置生成融合这两个来源的令牌。

## 输入参数

| 参数 | 数据类型 | 必需 | 取值范围 | 描述 |
|------|-----------|------|----------|-------------|
| `clip` | CLIP | 是 | - | 用于令牌化和编码的 CLIP 模型 |
| `clip视觉输出` | CLIP_VISION_OUTPUT | 是 | - | 来自 CLIP 视觉模型的视觉嵌入，提供图像上下文 |
| `提示` | STRING | 是 | - | 指导视频生成的文本描述，支持多行输入和动态提示 |
| `图像交错` | INT | 是 | 1-512 | 图像相对于文本提示的影响程度。数值越高表示文本提示的影响越大。（默认值：2） |

## 输出结果

| 输出名称 | 数据类型 | 描述 |
|----------|-----------|-------------|
| `CONDITIONING` | CONDITIONING | 结合文本和图像信息用于视频生成的条件数据 |
