> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/LatentApplyOperationCFG/zh.md)

## 概述

LatentApplyOperationCFG 节点通过应用潜在操作来修改模型中的条件引导过程。该节点的工作原理是在无分类器引导（CFG）采样过程中拦截条件输出，并在潜在表示被用于生成之前对其应用指定操作。

## 输入

| 参数 | 数据类型 | 必需 | 取值范围 | 描述 |
|-----------|-----------|----------|-------|-------------|
| `模型` | MODEL | 是 | - | 将应用 CFG 操作的模型 |
| `操作` | LATENT_OPERATION | 是 | - | 在 CFG 采样过程中要应用的潜在操作 |

## 输出

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `模型` | MODEL | 已在其采样过程中应用 CFG 操作的修改后模型 |
