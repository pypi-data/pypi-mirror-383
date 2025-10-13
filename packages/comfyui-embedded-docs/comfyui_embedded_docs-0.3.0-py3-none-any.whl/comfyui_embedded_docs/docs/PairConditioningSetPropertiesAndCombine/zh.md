> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/PairConditioningSetPropertiesAndCombine/zh.md)

PairConditioningSetPropertiesAndCombine 节点通过将新的条件数据应用到现有的正向和负向条件输入，来修改并组合条件对。它允许您调整所应用条件数据的强度，并控制条件区域的设置方式。该节点在需要将多个条件源混合在一起的高级条件处理工作流中特别有用。

## 输入参数

| 参数名 | 数据类型 | 必填 | 取值范围 | 描述 |
|-----------|-----------|----------|-------|-------------|
| `正面条件` | CONDITIONING | 是 | - | 原始的正向条件输入 |
| `负面条件` | CONDITIONING | 是 | - | 原始的负向条件输入 |
| `新正面条件` | CONDITIONING | 是 | - | 要应用的新正向条件数据 |
| `新负面条件` | CONDITIONING | 是 | - | 要应用的新负向条件数据 |
| `强度` | FLOAT | 是 | 0.0 到 10.0 | 应用新条件数据的强度因子（默认值：1.0） |
| `设置条件区域` | STRING | 是 | "default"<br>"mask bounds" | 控制条件数据的应用方式 |
| `遮罩` | MASK | 否 | - | 用于限制条件数据应用区域的可选遮罩 |
| `约束` | HOOKS | 否 | - | 用于高级控制的可选钩子组 |
| `间隔` | TIMESTEPS_RANGE | 否 | - | 可选的时间步范围规范 |

## 输出结果

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `负面条件` | CONDITIONING | 组合后的正向条件输出 |
| `负面条件` | CONDITIONING | 组合后的负向条件输出 |
