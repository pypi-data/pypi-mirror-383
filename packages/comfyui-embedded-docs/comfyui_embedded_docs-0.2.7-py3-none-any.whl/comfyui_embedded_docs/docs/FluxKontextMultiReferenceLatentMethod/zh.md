> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/FluxKontextMultiReferenceLatentMethod/zh.md)

## 概述

FluxKontextMultiReferenceLatentMethod 节点通过设置特定的参考潜空间方法来修改条件数据。它会将选定的方法附加到条件输入中，从而影响后续生成步骤中参考潜空间的处理方式。该节点标记为实验性功能，属于 Flux 条件系统的一部分。

## 输入

| 参数 | 数据类型 | 必填 | 取值范围 | 描述 |
|-----------|-----------|----------|-------|-------------|
| `conditioning` | CONDITIONING | 是 | - | 需要应用参考潜空间方法进行修改的条件数据 |
| `reference_latents_method` | STRING | 是 | `"offset"`<br>`"index"`<br>`"uxo/uno"` | 用于参考潜空间处理的方法。如果选择 "uxo" 或 "uso"，将被转换为 "uxo" |

## 输出

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `conditioning` | CONDITIONING | 已应用参考潜空间方法的修改后条件数据 |
