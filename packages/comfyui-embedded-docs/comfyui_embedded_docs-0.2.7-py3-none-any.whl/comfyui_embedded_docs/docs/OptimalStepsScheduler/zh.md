> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/OptimalStepsScheduler/zh.md)

## 概述

OptimalStepsScheduler 节点根据所选模型类型和步数配置，为扩散模型计算噪声调度 sigma 值。它会根据去噪参数调整总步数，并插值噪声级别以匹配请求的步数。该节点返回一个 sigma 值序列，用于确定扩散采样过程中使用的噪声水平。

## 输入

| 参数 | 数据类型 | 必填 | 取值范围 | 描述 |
|-----------|-----------|----------|-------|-------------|
| `model_type` | COMBO | 是 | "FLUX"<br>"Wan"<br>"Chroma" | 用于噪声级别计算的扩散模型类型 |
| `步数` | INT | 是 | 3-1000 | 要计算的采样总步数（默认值：20） |
| `去噪` | FLOAT | 否 | 0.0-1.0 | 控制去噪强度，调整有效步数（默认值：1.0） |

**注意：** 当 `denoise` 设置为小于 1.0 时，节点计算有效步数为 `steps * denoise`。如果 `denoise` 设置为 0.0，节点将返回空张量。

## 输出

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `sigmas` | SIGMAS | 表示扩散采样噪声调度的 sigma 值序列 |
