> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/LoraSave/zh.md)

LoraSave 节点从模型差异中提取并保存 LoRA（低秩自适应）文件。它可以处理扩散模型差异、文本编码器差异或两者，将它们转换为具有指定秩和类型的 LoRA 格式。生成的 LoRA 文件将保存到输出目录中，供后续使用。

## 输入参数

| 参数 | 数据类型 | 必填 | 取值范围 | 描述 |
|------|-----------|------|----------|------|
| `文件名前缀` | STRING | 是 | - | 输出文件名的前缀（默认："loras/ComfyUI_extracted_lora"） |
| `排名` | INT | 是 | 1-4096 | LoRA 的秩值，控制大小和复杂度（默认：8） |
| `lora类型` | COMBO | 是 | 多个可用选项 | 要创建的 LoRA 类型，提供多种可用选项 |
| `偏差差异` | BOOLEAN | 是 | - | 是否在 LoRA 计算中包含偏置差异（默认：True） |
| `模型差异` | MODEL | 否 | - | 要转换为 lora 的 ModelSubtract 输出 |
| `文本编码器差异` | CLIP | 否 | - | 要转换为 lora 的 CLIPSubtract 输出 |

**注意：** 要使节点正常工作，必须至少提供 `model_diff` 或 `text_encoder_diff` 中的一个参数。如果两者都未提供，节点将不会产生任何输出。

## 输出结果

| 输出名称 | 数据类型 | 描述 |
|----------|-----------|------|
| - | - | 此节点将 LoRA 文件保存到输出目录，但不会通过工作流返回任何数据 |
