> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/ExtendIntermediateSigmas/zh.md)

ExtendIntermediateSigmas 节点接收现有的 sigma 值序列，并在它们之间插入额外的中间 sigma 值。它允许您指定要添加的额外步数、用于插值的间距方法，以及可选的起始和结束 sigma 边界，以控制在 sigma 序列中进行扩展的位置。

## 输入参数

| 参数名 | 数据类型 | 必填 | 取值范围 | 描述 |
|-----------|-----------|----------|-------|-------------|
| `sigmas` | SIGMAS | 是 | - | 要插入中间值的输入 sigma 序列 |
| `步数` | INT | 是 | 1-100 | 在现有 sigma 值之间插入的中间步数（默认值：2） |
| `起始 sigma` | FLOAT | 是 | -1.0 到 20000.0 | 扩展的上限 sigma 边界 - 仅扩展低于此值的 sigma（默认值：-1.0，表示无穷大） |
| `结束 sigma` | FLOAT | 是 | 0.0 到 20000.0 | 扩展的下限 sigma 边界 - 仅扩展高于此值的 sigma（默认值：12.0） |
| `间距` | COMBO | 是 | "linear"<br>"cosine"<br>"sine" | 用于中间 sigma 值间距的插值方法 |

**注意：** 该节点仅在满足当前 sigma 小于等于 `start_at_sigma` 且大于等于 `end_at_sigma` 条件的现有 sigma 对之间插入中间 sigma 值。当 `start_at_sigma` 设置为 -1.0 时，它被视为无穷大，这意味着仅应用 `end_at_sigma` 下限边界。

## 输出参数

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `sigmas` | SIGMAS | 插入了额外中间值的扩展 sigma 序列 |
