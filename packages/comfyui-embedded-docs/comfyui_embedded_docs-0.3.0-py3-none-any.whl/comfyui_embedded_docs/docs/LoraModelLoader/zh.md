> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/LoraModelLoader/zh.md)

LoraModelLoader 节点将训练好的 LoRA（低秩自适应）权重应用于扩散模型。它通过从训练好的 LoRA 模型加载权重并调整其影响强度来修改基础模型。这使您能够定制扩散模型的行为，而无需从头开始重新训练。

## 输入参数

| 参数 | 数据类型 | 必需 | 取值范围 | 描述 |
|-----------|-----------|----------|-------|-------------|
| `model` | MODEL | 是 | - | 要应用 LoRA 的扩散模型。 |
| `lora` | LORA_MODEL | 是 | - | 要应用于扩散模型的 LoRA 模型。 |
| `strength_model` | FLOAT | 是 | -100.0 到 100.0 | 修改扩散模型的强度。该值可以为负数（默认值：1.0）。 |

**注意：** 当 `strength_model` 设置为 0 时，节点将返回原始模型，不应用任何 LoRA 修改。

## 输出结果

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `model` | MODEL | 应用了 LoRA 权重后的修改版扩散模型。 |
