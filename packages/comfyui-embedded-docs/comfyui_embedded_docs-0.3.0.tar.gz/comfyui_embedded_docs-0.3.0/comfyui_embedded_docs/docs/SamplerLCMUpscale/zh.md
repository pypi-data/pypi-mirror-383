> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/SamplerLCMUpscale/zh.md)

> 本文档由 AI 生成。如果您发现任何错误或有改进建议，请随时贡献！[在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/SamplerLCMUpscale/en.md)

SamplerLCMUpscale 节点提供了一种专门的采样方法，将潜在一致性模型（LCM）采样与图像放大功能相结合。它允许您在采样过程中使用各种插值方法放大图像，有助于在保持图像质量的同时生成更高分辨率的输出。

## 输入参数

| 参数 | 数据类型 | 必填 | 取值范围 | 描述 |
|------|-----------|------|----------|------|
| `缩放比例` | FLOAT | 否 | 0.1 - 20.0 | 放大过程中应用的缩放因子（默认：1.0） |
| `缩放步数` | INT | 否 | -1 - 1000 | 放大过程使用的步数。使用 -1 表示自动计算（默认：-1） |
| `缩放方法` | COMBO | 是 | "bislerp"<br>"nearest-exact"<br>"bilinear"<br>"area"<br>"bicubic" | 用于图像放大的插值方法 |

## 输出结果

| 输出名称 | 数据类型 | 描述 |
|----------|-----------|------|
| `sampler` | SAMPLER | 返回一个配置好的采样器对象，可在采样管道中使用 |
