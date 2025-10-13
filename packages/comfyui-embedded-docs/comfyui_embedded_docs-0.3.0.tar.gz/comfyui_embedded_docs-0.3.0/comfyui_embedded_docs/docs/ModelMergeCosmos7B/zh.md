> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/ModelMergeCosmos7B/zh.md)

ModelMergeCosmos7B 节点通过特定组件的加权混合将两个 AI 模型合并在一起。它允许通过调整位置嵌入、Transformer 块和最终层的独立权重，来精细控制模型不同部分的融合方式。

## 输入参数

| 参数 | 数据类型 | 必填 | 取值范围 | 描述 |
|------|-----------|------|----------|------|
| `模型1` | MODEL | 是 | - | 要合并的第一个模型 |
| `模型2` | MODEL | 是 | - | 要合并的第二个模型 |
| `pos_embedder.` | FLOAT | 是 | 0.0 - 1.0 | 位置嵌入器组件的权重（默认：1.0） |
| `extra_pos_embedder.` | FLOAT | 是 | 0.0 - 1.0 | 额外位置嵌入器组件的权重（默认：1.0） |
| `x_embedder.` | FLOAT | 是 | 0.0 - 1.0 | x 嵌入器组件的权重（默认：1.0） |
| `t_embedder.` | FLOAT | 是 | 0.0 - 1.0 | t 嵌入器组件的权重（默认：1.0） |
| `affline_norm.` | FLOAT | 是 | 0.0 - 1.0 | 仿射归一化组件的权重（默认：1.0） |
| `blocks.block0.` | FLOAT | 是 | 0.0 - 1.0 | Transformer 块 0 的权重（默认：1.0） |
| `blocks.block1.` | FLOAT | 是 | 0.0 - 1.0 | Transformer 块 1 的权重（默认：1.0） |
| `blocks.block2.` | FLOAT | 是 | 0.0 - 1.0 | Transformer 块 2 的权重（默认：1.0） |
| `blocks.block3.` | FLOAT | 是 | 0.0 - 1.0 | Transformer 块 3 的权重（默认：1.0） |
| `blocks.block4.` | FLOAT | 是 | 0.0 - 1.0 | Transformer 块 4 的权重（默认：1.0） |
| `blocks.block5.` | FLOAT | 是 | 0.0 - 1.0 | Transformer 块 5 的权重（默认：1.0） |
| `blocks.block6.` | FLOAT | 是 | 0.0 - 1.0 | Transformer 块 6 的权重（默认：1.0） |
| `blocks.block7.` | FLOAT | 是 | 0.0 - 1.0 | Transformer 块 7 的权重（默认：1.0） |
| `blocks.block8.` | FLOAT | 是 | 0.0 - 1.0 | Transformer 块 8 的权重（默认：1.0） |
| `blocks.block9.` | FLOAT | 是 | 0.0 - 1.0 | Transformer 块 9 的权重（默认：1.0） |
| `blocks.block10.` | FLOAT | 是 | 0.0 - 1.0 | Transformer 块 10 的权重（默认：1.0） |
| `blocks.block11.` | FLOAT | 是 | 0.0 - 1.0 | Transformer 块 11 的权重（默认：1.0） |
| `blocks.block12.` | FLOAT | 是 | 0.0 - 1.0 | Transformer 块 12 的权重（默认：1.0） |
| `blocks.block13.` | FLOAT | 是 | 0.0 - 1.0 | Transformer 块 13 的权重（默认：1.0） |
| `blocks.block14.` | FLOAT | 是 | 0.0 - 1.0 | Transformer 块 14 的权重（默认：1.0） |
| `blocks.block15.` | FLOAT | 是 | 0.0 - 1.0 | Transformer 块 15 的权重（默认：1.0） |
| `blocks.block16.` | FLOAT | 是 | 0.0 - 1.0 | Transformer 块 16 的权重（默认：1.0） |
| `blocks.block17.` | FLOAT | 是 | 0.0 - 1.0 | Transformer 块 17 的权重（默认：1.0） |
| `blocks.block18.` | FLOAT | 是 | 0.0 - 1.0 | Transformer 块 18 的权重（默认：1.0） |
| `blocks.block19.` | FLOAT | 是 | 0.0 - 1.0 | Transformer 块 19 的权重（默认：1.0） |
| `blocks.block20.` | FLOAT | 是 | 0.0 - 1.0 | Transformer 块 20 的权重（默认：1.0） |
| `blocks.block21.` | FLOAT | 是 | 0.0 - 1.0 | Transformer 块 21 的权重（默认：1.0） |
| `blocks.block22.` | FLOAT | 是 | 0.0 - 1.0 | Transformer 块 22 的权重（默认：1.0） |
| `blocks.block23.` | FLOAT | 是 | 0.0 - 1.0 | Transformer 块 23 的权重（默认：1.0） |
| `blocks.block24.` | FLOAT | 是 | 0.0 - 1.0 | Transformer 块 24 的权重（默认：1.0） |
| `blocks.block25.` | FLOAT | 是 | 0.0 - 1.0 | Transformer 块 25 的权重（默认：1.0） |
| `blocks.block26.` | FLOAT | 是 | 0.0 - 1.0 | Transformer 块 26 的权重（默认：1.0） |
| `blocks.block27.` | FLOAT | 是 | 0.0 - 1.0 | Transformer 块 27 的权重（默认：1.0） |
| `final_layer.` | FLOAT | 是 | 0.0 - 1.0 | 最终层组件的权重（默认：1.0） |

## 输出结果

| 输出名称 | 数据类型 | 描述 |
|----------|-----------|------|
| `model` | MODEL | 融合了两个输入模型特征的合并模型 |
