> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/StableCascade_StageC_VAEEncode/zh.md)

## 概述

StableCascade_StageC_VAEEncode 节点通过 VAE 编码器处理图像，为 Stable Cascade 模型生成潜在表示。它接收输入图像并使用指定的 VAE 模型进行压缩，然后输出两个潜在表示：一个用于阶段 C，另一个是阶段 B 的占位符。压缩参数控制在编码前图像被缩小的程度。

## 输入

| 参数 | 数据类型 | 必需 | 范围 | 描述 |
|-----------|-----------|----------|-------|-------------|
| `图像` | IMAGE | 是 | - | 需要编码到潜在空间的输入图像 |
| `vae` | VAE | 是 | - | 用于图像编码的 VAE 模型 |
| `压缩` | INT | 否 | 4-128 | 编码前应用于图像的压缩因子（默认值：42） |

## 输出

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `阶段B` | LATENT | 为 Stable Cascade 模型阶段 C 编码的潜在表示 |
| `stage_b` | LATENT | 阶段 B 的占位符潜在表示（当前返回零值） |
