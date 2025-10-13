> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/EmptyHunyuanImageLatent/zh.md)

## 概述

EmptyHunyuanImageLatent 节点创建一个具有特定维度的空潜在张量，用于混元图像生成模型。它生成一个空白的起始点，可以在工作流中通过后续节点进行处理。该节点允许您指定潜在空间的宽度、高度和批次大小。

## 输入

| 参数 | 数据类型 | 必需 | 取值范围 | 描述 |
|-----------|-----------|----------|-------|-------------|
| `width` | INT | 是 | 64 到 MAX_RESOLUTION | 生成潜在图像的宽度，单位为像素（默认值：2048，步长：32） |
| `height` | INT | 是 | 64 到 MAX_RESOLUTION | 生成潜在图像的高度，单位为像素（默认值：2048，步长：32） |
| `batch_size` | INT | 是 | 1 到 4096 | 批次中生成的潜在样本数量（默认值：1） |

## 输出

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `LATENT` | LATENT | 具有指定维度的空潜在张量，用于混元图像处理 |
