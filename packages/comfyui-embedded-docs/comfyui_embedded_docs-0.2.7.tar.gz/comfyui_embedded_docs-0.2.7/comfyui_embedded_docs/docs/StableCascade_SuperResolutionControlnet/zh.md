> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/StableCascade_SuperResolutionControlnet/zh.md)

## 概述

StableCascade_SuperResolutionControlnet 节点为 Stable Cascade 超分辨率处理准备输入数据。它接收输入图像并使用 VAE 进行编码以创建控制网络输入，同时为 Stable Cascade 流程的 C 阶段和 B 阶段生成占位符潜在表示。

## 输入

| 参数 | 数据类型 | 必需 | 取值范围 | 描述 |
|-----------|-----------|----------|-------|-------------|
| `图像` | IMAGE | 是 | - | 用于超分辨率处理的输入图像 |
| `vae` | VAE | 是 | - | 用于编码输入图像的 VAE 模型 |

## 输出

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `阶段C` | IMAGE | 适用于控制网络输入的编码图像表示 |
| `阶段B` | LATENT | 用于 Stable Cascade 处理 C 阶段的占位符潜在表示 |
| `stage_b` | LATENT | 用于 Stable Cascade 处理 B 阶段的占位符潜在表示 |
