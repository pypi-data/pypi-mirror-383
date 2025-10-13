> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/CLIPTextEncodeControlnet/zh.md)

CLIPTextEncodeControlnet 节点使用 CLIP 模型处理文本输入，并将其与现有的条件数据相结合，为 controlnet 应用创建增强的条件输出。该节点将输入文本进行标记化处理，通过 CLIP 模型进行编码，并将生成的嵌入作为交叉注意力 controlnet 参数添加到提供的条件数据中。

## 输入参数

| 参数名 | 数据类型 | 输入类型 | 默认值 | 数值范围 | 描述 |
|-----------|-----------|------------|---------|-------|-------------|
| `clip` | CLIP | 必需 | - | - | 用于文本标记化和编码的 CLIP 模型 |
| `条件` | CONDITIONING | 必需 | - | - | 需要通过 controlnet 参数增强的现有条件数据 |
| `文本` | STRING | 多行文本，动态提示 | - | - | 由 CLIP 模型处理的文本输入 |

**注意：** 此节点需要同时提供 `clip` 和 `conditioning` 输入才能正常工作。`text` 输入支持动态提示和多行文本，以实现灵活的文本处理。

## 输出结果

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `CONDITIONING` | CONDITIONING | 添加了 controlnet 交叉注意力参数的增强条件数据 |
