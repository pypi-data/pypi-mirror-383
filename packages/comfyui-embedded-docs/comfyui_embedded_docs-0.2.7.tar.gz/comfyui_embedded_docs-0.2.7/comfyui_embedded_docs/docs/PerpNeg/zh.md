> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/PerpNeg/zh.md)

> 该文档由 AI 生成，如果您发现任何错误或有改进建议，请随时贡献！[在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/PerpNeg/en.md)

PerpNeg 节点对模型的采样过程应用垂直负向引导。该节点通过修改模型的配置函数，使用负向条件和缩放因子来调整噪声预测。此节点已被弃用，并由功能更完善的 PerpNegGuider 节点替代。

## 输入参数

| 参数 | 数据类型 | 必需 | 取值范围 | 描述 |
|------|-----------|------|----------|------|
| `模型` | MODEL | 是 | - | 要应用垂直负向引导的模型 |
| `空条件` | CONDITIONING | 是 | - | 用于负向引导计算的空条件 |
| `负面缩放` | FLOAT | 否 | 0.0 - 100.0 | 负向引导的缩放因子（默认值：1.0） |

## 输出结果

| 输出名称 | 数据类型 | 描述 |
|----------|-----------|------|
| `模型` | MODEL | 应用了垂直负向引导的修改后模型 |

**注意**：此节点已被弃用，并已由 PerpNegGuider 节点替代。它被标记为实验性功能，不应在生产工作流中使用。
