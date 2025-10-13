> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/SaveLoRANode/zh.md)

SaveLoRA 节点可将 LoRA（低秩自适应）模型保存至输出目录。该节点接收 LoRA 模型作为输入，并生成带有自动生成文件名的 safetensors 文件。您可自定义文件名前缀，并可选地在文件名中包含训练步数以便更好地进行组织管理。

## 输入参数

| 参数名 | 数据类型 | 必需 | 取值范围 | 描述 |
|--------|----------|------|----------|------|
| `lora` | LORA_MODEL | 是 | - | 待保存的 LoRA 模型。请勿使用带有 LoRA 层的模型。 |
| `prefix` | STRING | 是 | - | 保存的 LoRA 文件使用的前缀（默认："loras/ComfyUI_trained_lora"）。 |
| `steps` | INT | 否 | - | 可选参数：LoRA 已训练的步数，用于命名保存的文件。 |

## 输出结果

| 输出名称 | 数据类型 | 描述 |
|----------|-----------|------|
| *无* | - | 该节点不返回任何输出，但会将 LoRA 模型保存到输出目录。 |
