> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/ConditioningTimestepsRange/zh.md)

ConditioningTimestepsRange 节点创建三个不同的时间步范围，用于控制在生成过程中应用条件效果的时机。它接收起始和结束百分比值，并将整个时间步范围（0.0 到 1.0）划分为三个区段：指定百分比之间的主范围、起始百分比之前的范围以及结束百分比之后的范围。

## 输入参数

| 参数 | 数据类型 | 必需 | 范围 | 描述 |
|-----------|-----------|----------|-------|-------------|
| `开始百分比` | FLOAT | 是 | 0.0 - 1.0 | 时间步范围的起始百分比（默认值：0.0） |
| `结束百分比` | FLOAT | 是 | 0.0 - 1.0 | 时间步范围的结束百分比（默认值：1.0） |

## 输出结果

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `范围前` | TIMESTEPS_RANGE | 由 start_percent 和 end_percent 定义的主时间步范围 |
| `范围后` | TIMESTEPS_RANGE | 从 0.0 到 start_percent 的时间步范围 |
| `AFTER_RANGE` | TIMESTEPS_RANGE | 从 end_percent 到 1.0 的时间步范围 |
