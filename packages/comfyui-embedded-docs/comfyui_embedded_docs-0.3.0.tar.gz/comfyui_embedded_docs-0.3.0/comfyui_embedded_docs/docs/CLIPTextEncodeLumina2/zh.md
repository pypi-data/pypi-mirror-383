> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/CLIPTextEncodeLumina2/zh.md)

> 本文档由 AI 生成。如果您发现任何错误或有改进建议，请随时贡献！[在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/CLIPTextEncodeLumina2/en.md)

CLIP Text Encode for Lumina2 节点使用 CLIP 模型将系统提示和用户提示编码为嵌入向量，该向量可以指导扩散模型生成特定图像。它将预定义的系统提示与您的自定义文本提示相结合，并通过 CLIP 模型进行处理，以创建用于图像生成的条件数据。

## 输入参数

| 参数名 | 数据类型 | 输入类型 | 默认值 | 取值范围 | 描述 |
|-----------|-----------|------------|---------|-------|-------------|
| `system_prompt` | STRING | COMBO | - | "superior", "alignment" | Lumina2 提供两种类型的系统提示：Superior：您是一个旨在根据文本提示或用户提示生成具有卓越图文对齐度的优质图像的助手。Alignment：您是一个旨在根据文本提示生成具有最高图文对齐度的高质量图像的助手。 |
| `user_prompt` | STRING | STRING | - | - | 需要编码的文本。 |
| `clip` | CLIP | CLIP | - | - | 用于文本编码的 CLIP 模型。 |

**注意：** `clip` 输入是必需的，不能为 None。如果 clip 输入无效，节点将引发错误，提示检查点可能不包含有效的 CLIP 或文本编码器模型。

## 输出结果

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `CONDITIONING` | CONDITIONING | 包含嵌入文本的条件数据，用于指导扩散模型。 |
