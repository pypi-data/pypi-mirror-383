> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/ModelMergeLTXV/zh.md)

ModelMergeLTXV 节点执行专为 LTXV 模型架构设计的高级模型合并操作。它允许您通过调整各种模型组件（包括 Transformer 块、投影层和其他专用模块）的插值权重，将两个不同的模型融合在一起。

## 输入参数

| 参数 | 数据类型 | 必需 | 范围 | 描述 |
|-----------|-----------|----------|-------|-------------|
| `模型1` | MODEL | 是 | - | 要合并的第一个模型 |
| `模型2` | MODEL | 是 | - | 要合并的第二个模型 |
| `patchify_proj.` | FLOAT | 是 | 0.0 - 1.0 | 分块投影层的插值权重（默认：1.0） |
| `adaln_single.` | FLOAT | 是 | 0.0 - 1.0 | 自适应层归一化单层的插值权重（默认：1.0） |
| `caption_projection.` | FLOAT | 是 | 0.0 - 1.0 | 标题投影层的插值权重（默认：1.0） |
| `transformer_blocks.0.` | FLOAT | 是 | 0.0 - 1.0 | Transformer 块 0 的插值权重（默认：1.0） |
| `transformer_blocks.1.` | FLOAT | 是 | 0.0 - 1.0 | Transformer 块 1 的插值权重（默认：1.0） |
| `transformer_blocks.2.` | FLOAT | 是 | 0.0 - 1.0 | Transformer 块 2 的插值权重（默认：1.0） |
| `transformer_blocks.3.` | FLOAT | 是 | 0.0 - 1.0 | Transformer 块 3 的插值权重（默认：1.0） |
| `transformer_blocks.4.` | FLOAT | 是 | 0.0 - 1.0 | Transformer 块 4 的插值权重（默认：1.0） |
| `transformer_blocks.5.` | FLOAT | 是 | 0.0 - 1.0 | Transformer 块 5 的插值权重（默认：1.0） |
| `transformer_blocks.6.` | FLOAT | 是 | 0.0 - 1.0 | Transformer 块 6 的插值权重（默认：1.0） |
| `transformer_blocks.7.` | FLOAT | 是 | 0.0 - 1.0 | Transformer 块 7 的插值权重（默认：1.0） |
| `transformer_blocks.8.` | FLOAT | 是 | 0.0 - 1.0 | Transformer 块 8 的插值权重（默认：1.0） |
| `transformer_blocks.9.` | FLOAT | 是 | 0.0 - 1.0 | Transformer 块 9 的插值权重（默认：1.0） |
| `transformer_blocks.10.` | FLOAT | 是 | 0.0 - 1.0 | Transformer 块 10 的插值权重（默认：1.0） |
| `transformer_blocks.11.` | FLOAT | 是 | 0.0 - 1.0 | Transformer 块 11 的插值权重（默认：1.0） |
| `transformer_blocks.12.` | FLOAT | 是 | 0.0 - 1.0 | Transformer 块 12 的插值权重（默认：1.0） |
| `transformer_blocks.13.` | FLOAT | 是 | 0.0 - 1.0 | Transformer 块 13 的插值权重（默认：1.0） |
| `transformer_blocks.14.` | FLOAT | 是 | 0.0 - 1.0 | Transformer 块 14 的插值权重（默认：1.0） |
| `transformer_blocks.15.` | FLOAT | 是 | 0.0 - 1.0 | Transformer 块 15 的插值权重（默认：1.0） |
| `transformer_blocks.16.` | FLOAT | 是 | 0.0 - 1.0 | Transformer 块 16 的插值权重（默认：1.0） |
| `transformer_blocks.17.` | FLOAT | 是 | 0.0 - 1.0 | Transformer 块 17 的插值权重（默认：1.0） |
| `transformer_blocks.18.` | FLOAT | 是 | 0.0 - 1.0 | Transformer 块 18 的插值权重（默认：1.0） |
| `transformer_blocks.19.` | FLOAT | 是 | 0.0 - 1.0 | Transformer 块 19 的插值权重（默认：1.0） |
| `transformer_blocks.20.` | FLOAT | 是 | 0.0 - 1.0 | Transformer 块 20 的插值权重（默认：1.0） |
| `transformer_blocks.21.` | FLOAT | 是 | 0.0 - 1.0 | Transformer 块 21 的插值权重（默认：1.0） |
| `transformer_blocks.22.` | FLOAT | 是 | 0.0 - 1.0 | Transformer 块 22 的插值权重（默认：1.0） |
| `transformer_blocks.23.` | FLOAT | 是 | 0.0 - 1.0 | Transformer 块 23 的插值权重（默认：1.0） |
| `transformer_blocks.24.` | FLOAT | 是 | 0.0 - 1.0 | Transformer 块 24 的插值权重（默认：1.0） |
| `transformer_blocks.25.` | FLOAT | 是 | 0.0 - 1.0 | Transformer 块 25 的插值权重（默认：1.0） |
| `transformer_blocks.26.` | FLOAT | 是 | 0.0 - 1.0 | Transformer 块 26 的插值权重（默认：1.0） |
| `transformer_blocks.27.` | FLOAT | 是 | 0.0 - 1.0 | Transformer 块 27 的插值权重（默认：1.0） |
| `scale_shift_table` | FLOAT | 是 | 0.0 - 1.0 | 尺度偏移表的插值权重（默认：1.0） |
| `proj_out.` | FLOAT | 是 | 0.0 - 1.0 | 投影输出层的插值权重（默认：1.0） |

## 输出结果

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `model` | MODEL | 根据指定的插值权重合并两个输入模型特征的融合模型 |
