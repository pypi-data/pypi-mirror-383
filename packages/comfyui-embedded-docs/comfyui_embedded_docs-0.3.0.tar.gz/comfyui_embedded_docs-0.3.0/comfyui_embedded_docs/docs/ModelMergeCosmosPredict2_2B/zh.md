> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/ModelMergeCosmosPredict2_2B/zh.md)

ModelMergeCosmosPredict2_2B 节点采用基于模块化的方法合并两个扩散模型，可对不同模型组件进行细粒度控制。该节点通过调整位置嵌入器、时间嵌入器、Transformer 模块和最终层的插值权重，允许您混合两个模型的特定部分。这为精确控制每个模型中不同架构组件对最终合并结果的贡献提供了可能。

## 输入参数

| 参数 | 数据类型 | 必需 | 取值范围 | 描述 |
|------|-----------|------|----------|------|
| `model1` | MODEL | 是 | - | 要合并的第一个模型 |
| `model2` | MODEL | 是 | - | 要合并的第二个模型 |
| `pos_embedder.` | FLOAT | 是 | 0.0 - 1.0 | 位置嵌入器插值权重（默认：1.0） |
| `x_embedder.` | FLOAT | 是 | 0.0 - 1.0 | 输入嵌入器插值权重（默认：1.0） |
| `t_embedder.` | FLOAT | 是 | 0.0 - 1.0 | 时间嵌入器插值权重（默认：1.0） |
| `t_embedding_norm.` | FLOAT | 是 | 0.0 - 1.0 | 时间嵌入归一化插值权重（默认：1.0） |
| `blocks.0.` | FLOAT | 是 | 0.0 - 1.0 | Transformer 模块 0 插值权重（默认：1.0） |
| `blocks.1.` | FLOAT | 是 | 0.0 - 1.0 | Transformer 模块 1 插值权重（默认：1.0） |
| `blocks.2.` | FLOAT | 是 | 0.0 - 1.0 | Transformer 模块 2 插值权重（默认：1.0） |
| `blocks.3.` | FLOAT | 是 | 0.0 - 1.0 | Transformer 模块 3 插值权重（默认：1.0） |
| `blocks.4.` | FLOAT | 是 | 0.0 - 1.0 | Transformer 模块 4 插值权重（默认：1.0） |
| `blocks.5.` | FLOAT | 是 | 0.0 - 1.0 | Transformer 模块 5 插值权重（默认：1.0） |
| `blocks.6.` | FLOAT | 是 | 0.0 - 1.0 | Transformer 模块 6 插值权重（默认：1.0） |
| `blocks.7.` | FLOAT | 是 | 0.0 - 1.0 | Transformer 模块 7 插值权重（默认：1.0） |
| `blocks.8.` | FLOAT | 是 | 0.0 - 1.0 | Transformer 模块 8 插值权重（默认：1.0） |
| `blocks.9.` | FLOAT | 是 | 0.0 - 1.0 | Transformer 模块 9 插值权重（默认：1.0） |
| `blocks.10.` | FLOAT | 是 | 0.0 - 1.0 | Transformer 模块 10 插值权重（默认：1.0） |
| `blocks.11.` | FLOAT | 是 | 0.0 - 1.0 | Transformer 模块 11 插值权重（默认：1.0） |
| `blocks.12.` | FLOAT | 是 | 0.0 - 1.0 | Transformer 模块 12 插值权重（默认：1.0） |
| `blocks.13.` | FLOAT | 是 | 0.0 - 1.0 | Transformer 模块 13 插值权重（默认：1.0） |
| `blocks.14.` | FLOAT | 是 | 0.0 - 1.0 | Transformer 模块 14 插值权重（默认：1.0） |
| `blocks.15.` | FLOAT | 是 | 0.0 - 1.0 | Transformer 模块 15 插值权重（默认：1.0） |
| `blocks.16.` | FLOAT | 是 | 0.0 - 1.0 | Transformer 模块 16 插值权重（默认：1.0） |
| `blocks.17.` | FLOAT | 是 | 0.0 - 1.0 | Transformer 模块 17 插值权重（默认：1.0） |
| `blocks.18.` | FLOAT | 是 | 0.0 - 1.0 | Transformer 模块 18 插值权重（默认：1.0） |
| `blocks.19.` | FLOAT | 是 | 0.0 - 1.0 | Transformer 模块 19 插值权重（默认：1.0） |
| `blocks.20.` | FLOAT | 是 | 0.0 - 1.0 | Transformer 模块 20 插值权重（默认：1.0） |
| `blocks.21.` | FLOAT | 是 | 0.0 - 1.0 | Transformer 模块 21 插值权重（默认：1.0） |
| `blocks.22.` | FLOAT | 是 | 0.0 - 1.0 | Transformer 模块 22 插值权重（默认：1.0） |
| `blocks.23.` | FLOAT | 是 | 0.0 - 1.0 | Transformer 模块 23 插值权重（默认：1.0） |
| `blocks.24.` | FLOAT | 是 | 0.0 - 1.0 | Transformer 模块 24 插值权重（默认：1.0） |
| `blocks.25.` | FLOAT | 是 | 0.0 - 1.0 | Transformer 模块 25 插值权重（默认：1.0） |
| `blocks.26.` | FLOAT | 是 | 0.0 - 1.0 | Transformer 模块 26 插值权重（默认：1.0） |
| `blocks.27.` | FLOAT | 是 | 0.0 - 1.0 | Transformer 模块 27 插值权重（默认：1.0） |
| `final_layer.` | FLOAT | 是 | 0.0 - 1.0 | 最终层插值权重（默认：1.0） |

## 输出结果

| 输出名称 | 数据类型 | 描述 |
|----------|-----------|------|
| `model` | MODEL | 融合了两个输入模型特征的合并模型 |
