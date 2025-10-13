> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/ModelMergeCosmos14B/zh.md)

ModelMergeCosmos14B 节点采用基于模块的融合方式，专门针对 Cosmos 14B 模型架构设计，用于合并两个AI模型。通过调整每个模型块和嵌入层的权重值（范围0.0至1.0），您可以混合两个模型的不同组件。

## 输入参数

| 参数 | 数据类型 | 必填 | 取值范围 | 描述 |
|------|-----------|------|----------|------|
| `模型1` | MODEL | 是 | - | 要合并的第一个模型 |
| `模型2` | MODEL | 是 | - | 要合并的第二个模型 |
| `pos_embedder.` | FLOAT | 是 | 0.0 - 1.0 | 位置嵌入器权重（默认：1.0） |
| `extra_pos_embedder.` | FLOAT | 是 | 0.0 - 1.0 | 额外位置嵌入器权重（默认：1.0） |
| `x_embedder.` | FLOAT | 是 | 0.0 - 1.0 | X嵌入器权重（默认：1.0） |
| `t_embedder.` | FLOAT | 是 | 0.0 - 1.0 | T嵌入器权重（默认：1.0） |
| `affline_norm.` | FLOAT | 是 | 0.0 - 1.0 | 仿射归一化权重（默认：1.0） |
| `blocks.block0.` | FLOAT | 是 | 0.0 - 1.0 | 块0权重（默认：1.0） |
| `blocks.block1.` | FLOAT | 是 | 0.0 - 1.0 | 块1权重（默认：1.0） |
| `blocks.block2.` | FLOAT | 是 | 0.0 - 1.0 | 块2权重（默认：1.0） |
| `blocks.block3.` | FLOAT | 是 | 0.0 - 1.0 | 块3权重（默认：1.0） |
| `blocks.block4.` | FLOAT | 是 | 0.0 - 1.0 | 块4权重（默认：1.0） |
| `blocks.block5.` | FLOAT | 是 | 0.0 - 1.0 | 块5权重（默认：1.0） |
| `blocks.block6.` | FLOAT | 是 | 0.0 - 1.0 | 块6权重（默认：1.0） |
| `blocks.block7.` | FLOAT | 是 | 0.0 - 1.0 | 块7权重（默认：1.0） |
| `blocks.block8.` | FLOAT | 是 | 0.0 - 1.0 | 块8权重（默认：1.0） |
| `blocks.block9.` | FLOAT | 是 | 0.0 - 1.0 | 块9权重（默认：1.0） |
| `blocks.block10.` | FLOAT | 是 | 0.0 - 1.0 | 块10权重（默认：1.0） |
| `blocks.block11.` | FLOAT | 是 | 0.0 - 1.0 | 块11权重（默认：1.0） |
| `blocks.block12.` | FLOAT | 是 | 0.0 - 1.0 | 块12权重（默认：1.0） |
| `blocks.block13.` | FLOAT | 是 | 0.0 - 1.0 | 块13权重（默认：1.0） |
| `blocks.block14.` | FLOAT | 是 | 0.0 - 1.0 | 块14权重（默认：1.0） |
| `blocks.block15.` | FLOAT | 是 | 0.0 - 1.0 | 块15权重（默认：1.0） |
| `blocks.block16.` | FLOAT | 是 | 0.0 - 1.0 | 块16权重（默认：1.0） |
| `blocks.block17.` | FLOAT | 是 | 0.0 - 1.0 | 块17权重（默认：1.0） |
| `blocks.block18.` | FLOAT | 是 | 0.0 - 1.0 | 块18权重（默认：1.0） |
| `blocks.block19.` | FLOAT | 是 | 0.0 - 1.0 | 块19权重（默认：1.0） |
| `blocks.block20.` | FLOAT | 是 | 0.0 - 1.0 | 块20权重（默认：1.0） |
| `blocks.block21.` | FLOAT | 是 | 0.0 - 1.0 | 块21权重（默认：1.0） |
| `blocks.block22.` | FLOAT | 是 | 0.0 - 1.0 | 块22权重（默认：1.0） |
| `blocks.block23.` | FLOAT | 是 | 0.0 - 1.0 | 块23权重（默认：1.0） |
| `blocks.block24.` | FLOAT | 是 | 0.0 - 1.0 | 块24权重（默认：1.0） |
| `blocks.block25.` | FLOAT | 是 | 0.0 - 1.0 | 块25权重（默认：1.0） |
| `blocks.block26.` | FLOAT | 是 | 0.0 - 1.0 | 块26权重（默认：1.0） |
| `blocks.block27.` | FLOAT | 是 | 0.0 - 1.0 | 块27权重（默认：1.0） |
| `blocks.block28.` | FLOAT | 是 | 0.0 - 1.0 | 块28权重（默认：1.0） |
| `blocks.block29.` | FLOAT | 是 | 0.0 - 1.0 | 块29权重（默认：1.0） |
| `blocks.block30.` | FLOAT | 是 | 0.0 - 1.0 | 块30权重（默认：1.0） |
| `blocks.block31.` | FLOAT | 是 | 0.0 - 1.0 | 块31权重（默认：1.0） |
| `blocks.block32.` | FLOAT | 是 | 0.0 - 1.0 | 块32权重（默认：1.0） |
| `blocks.block33.` | FLOAT | 是 | 0.0 - 1.0 | 块33权重（默认：1.0） |
| `blocks.block34.` | FLOAT | 是 | 0.0 - 1.0 | 块34权重（默认：1.0） |
| `blocks.block35.` | FLOAT | 是 | 0.0 - 1.0 | 块35权重（默认：1.0） |
| `final_layer.` | FLOAT | 是 | 0.0 - 1.0 | 最终层权重（默认：1.0） |

## 输出结果

| 输出名称 | 数据类型 | 描述 |
|----------|-----------|------|
| `model` | MODEL | 融合了两个输入模型特征的合并模型 |
