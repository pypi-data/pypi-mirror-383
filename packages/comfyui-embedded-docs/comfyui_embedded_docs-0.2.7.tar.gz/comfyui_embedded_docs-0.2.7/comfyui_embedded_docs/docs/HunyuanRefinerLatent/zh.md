> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/HunyuanRefinerLatent/zh.md)

HunyuanRefinerLatent 节点用于处理精炼操作中的条件输入和潜空间输入。该节点对正负条件输入同时应用噪声增强，并结合潜空间图像数据，生成具有特定维度的新潜空间输出以供后续处理。

## 输入参数

| 参数名称 | 数据类型 | 必填 | 取值范围 | 描述 |
|-----------|-----------|----------|-------|-------------|
| `positive` | CONDITIONING | 是 | - | 待处理的正向条件输入 |
| `negative` | CONDITIONING | 是 | - | 待处理的负向条件输入 |
| `latent` | LATENT | 是 | - | 潜空间表示输入 |
| `noise_augmentation` | FLOAT | 是 | 0.0 - 1.0 | 应用的噪声增强量（默认值：0.10） |

## 输出参数

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `positive` | CONDITIONING | 经过噪声增强和潜空间图像拼接处理后的正向条件 |
| `negative` | CONDITIONING | 经过噪声增强和潜空间图像拼接处理后的负向条件 |
| `latent` | LATENT | 具有 [batch_size, 32, height, width, channels] 维度的新潜空间输出 |
