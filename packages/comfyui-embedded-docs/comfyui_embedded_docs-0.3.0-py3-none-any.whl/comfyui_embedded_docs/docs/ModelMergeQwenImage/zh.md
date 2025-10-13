> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/ModelMergeQwenImage/zh.md)

ModelMergeQwenImage 节点通过以可调节的权重组合两个 AI 模型的组件来合并它们。该节点允许您混合 Qwen 图像模型的特定部分，包括 Transformer 块、位置嵌入和文本处理组件。您可以控制每个模型在合并结果的不同部分中所具有的影响力。

## 输入参数

| 参数 | 数据类型 | 必需 | 取值范围 | 描述 |
|-----------|-----------|----------|-------|-------------|
| `model1` | MODEL | 是 | - | 要合并的第一个模型（默认：无） |
| `model2` | MODEL | 是 | - | 要合并的第二个模型（默认：无） |
| `pos_embeds.` | FLOAT | 是 | 0.0 到 1.0 | 位置嵌入混合的权重（默认：1.0） |
| `img_in.` | FLOAT | 是 | 0.0 到 1.0 | 图像输入处理混合的权重（默认：1.0） |
| `txt_norm.` | FLOAT | 是 | 0.0 到 1.0 | 文本归一化混合的权重（默认：1.0） |
| `txt_in.` | FLOAT | 是 | 0.0 到 1.0 | 文本输入处理混合的权重（默认：1.0） |
| `time_text_embed.` | FLOAT | 是 | 0.0 到 1.0 | 时间和文本嵌入混合的权重（默认：1.0） |
| `transformer_blocks.0.` 到 `transformer_blocks.59.` | FLOAT | 是 | 0.0 到 1.0 | 每个 Transformer 块混合的权重（默认：1.0） |
| `proj_out.` | FLOAT | 是 | 0.0 到 1.0 | 输出投影混合的权重（默认：1.0） |

## 输出结果

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `model` | MODEL | 合并后的模型，包含来自两个输入模型组件按指定权重组合的结果 |
