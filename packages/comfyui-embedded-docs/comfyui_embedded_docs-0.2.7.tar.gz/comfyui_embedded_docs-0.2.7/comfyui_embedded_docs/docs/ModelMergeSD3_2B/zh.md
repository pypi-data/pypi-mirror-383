> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/ModelMergeSD3_2B/zh.md)

ModelMergeSD3_2B 节点允许您通过以可调节的权重混合两个 Stable Diffusion 3 2B 模型的组件来合并它们。该节点提供了对嵌入层和 Transformer 块的独立控制，从而能够为专门的生成任务进行精细调整的模型组合。

## 输入参数

| 参数 | 数据类型 | 必填 | 取值范围 | 描述 |
|-----------|-----------|----------|-------|-------------|
| `模型1` | MODEL | 是 | - | 要合并的第一个模型 |
| `模型2` | MODEL | 是 | - | 要合并的第二个模型 |
| `pos_embed.` | FLOAT | 是 | 0.0 - 1.0 | 位置嵌入插值权重（默认：1.0） |
| `x_embedder.` | FLOAT | 是 | 0.0 - 1.0 | 输入嵌入插值权重（默认：1.0） |
| `context_embedder.` | FLOAT | 是 | 0.0 - 1.0 | 上下文嵌入插值权重（默认：1.0） |
| `y_embedder.` | FLOAT | 是 | 0.0 - 1.0 | Y 嵌入插值权重（默认：1.0） |
| `t_embedder.` | FLOAT | 是 | 0.0 - 1.0 | 时间嵌入插值权重（默认：1.0） |
| `joint_blocks.0.` | FLOAT | 是 | 0.0 - 1.0 | 联合块 0 插值权重（默认：1.0） |
| `joint_blocks.1.` | FLOAT | 是 | 0.0 - 1.0 | 联合块 1 插值权重（默认：1.0） |
| `joint_blocks.2.` | FLOAT | 是 | 0.0 - 1.0 | 联合块 2 插值权重（默认：1.0） |
| `joint_blocks.3.` | FLOAT | 是 | 0.0 - 1.0 | 联合块 3 插值权重（默认：1.0） |
| `joint_blocks.4.` | FLOAT | 是 | 0.0 - 1.0 | 联合块 4 插值权重（默认：1.0） |
| `joint_blocks.5.` | FLOAT | 是 | 0.0 - 1.0 | 联合块 5 插值权重（默认：1.0） |
| `joint_blocks.6.` | FLOAT | 是 | 0.0 - 1.0 | 联合块 6 插值权重（默认：1.0） |
| `joint_blocks.7.` | FLOAT | 是 | 0.0 - 1.0 | 联合块 7 插值权重（默认：1.0） |
| `joint_blocks.8.` | FLOAT | 是 | 0.0 - 1.0 | 联合块 8 插值权重（默认：1.0） |
| `joint_blocks.9.` | FLOAT | 是 | 0.0 - 1.0 | 联合块 9 插值权重（默认：1.0） |
| `joint_blocks.10.` | FLOAT | 是 | 0.0 - 1.0 | 联合块 10 插值权重（默认：1.0） |
| `joint_blocks.11.` | FLOAT | 是 | 0.0 - 1.0 | 联合块 11 插值权重（默认：1.0） |
| `joint_blocks.12.` | FLOAT | 是 | 0.0 - 1.0 | 联合块 12 插值权重（默认：1.0） |
| `joint_blocks.13.` | FLOAT | 是 | 0.0 - 1.0 | 联合块 13 插值权重（默认：1.0） |
| `joint_blocks.14.` | FLOAT | 是 | 0.0 - 1.0 | 联合块 14 插值权重（默认：1.0） |
| `joint_blocks.15.` | FLOAT | 是 | 0.0 - 1.0 | 联合块 15 插值权重（默认：1.0） |
| `joint_blocks.16.` | FLOAT | 是 | 0.0 - 1.0 | 联合块 16 插值权重（默认：1.0） |
| `joint_blocks.17.` | FLOAT | 是 | 0.0 - 1.0 | 联合块 17 插值权重（默认：1.0） |
| `joint_blocks.18.` | FLOAT | 是 | 0.0 - 1.0 | 联合块 18 插值权重（默认：1.0） |
| `joint_blocks.19.` | FLOAT | 是 | 0.0 - 1.0 | 联合块 19 插值权重（默认：1.0） |
| `joint_blocks.20.` | FLOAT | 是 | 0.0 - 1.0 | 联合块 20 插值权重（默认：1.0） |
| `joint_blocks.21.` | FLOAT | 是 | 0.0 - 1.0 | 联合块 21 插值权重（默认：1.0） |
| `joint_blocks.22.` | FLOAT | 是 | 0.0 - 1.0 | 联合块 22 插值权重（默认：1.0） |
| `joint_blocks.23.` | FLOAT | 是 | 0.0 - 1.0 | 联合块 23 插值权重（默认：1.0） |
| `final_layer.` | FLOAT | 是 | 0.0 - 1.0 | 最终层插值权重（默认：1.0） |

## 输出结果

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `model` | MODEL | 合并后的模型，结合了两个输入模型的特征 |
