> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/PerturbedAttentionGuidance/zh.md)

# PerturbedAttentionGuidance

PerturbedAttentionGuidance 节点对扩散模型应用扰动注意力引导，以提升生成质量。该技术在采样过程中通过将模型的自注意力机制替换为专注于值投影的简化版本，从而调整条件去噪过程，有助于提高生成图像的连贯性和质量。

## 输入参数

| 参数 | 数据类型 | 必填 | 取值范围 | 描述 |
|------|-----------|------|----------|------|
| `模型` | MODEL | 是 | - | 要应用扰动注意力引导的扩散模型 |
| `规模` | FLOAT | 否 | 0.0 - 100.0 | 扰动注意力引导效果的强度（默认值：3.0） |

## 输出结果

| 输出名称 | 数据类型 | 描述 |
|----------|-----------|------|
| `模型` | MODEL | 应用了扰动注意力引导的修改后模型 |
