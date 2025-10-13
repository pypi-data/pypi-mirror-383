> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/TrimVideoLatent/zh.md)

> 本文档由 AI 生成，如果您发现任何错误或有改进建议，请随时贡献！[在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/TrimVideoLatent/en.md)

TrimVideoLatent 节点从视频潜在表示的起始位置移除帧。它接收一个潜在视频样本，并从开始处裁剪指定数量的帧，返回视频的剩余部分。这使您能够通过移除初始帧来缩短视频序列。

## 输入参数

| 参数 | 数据类型 | 必填 | 取值范围 | 描述 |
|-----------|-----------|----------|-------|-------------|
| `samples` | LATENT | 是 | - | 输入的视频潜在表示，包含待裁剪的帧 |
| `trim_amount` | INT | 否 | 0 至 99999 | 从视频起始位置移除的帧数量（默认值：0） |

## 输出参数

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `output` | LATENT | 经过裁剪的潜在视频表示，已从起始位置移除指定数量的帧 |
