> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/PairConditioningSetProperties/zh.md)

PairConditioningSetProperties 节点允许您同时修改正向和负向条件对属性。该节点会对两个条件输入同时应用强度调整、条件区域设置以及可选的遮罩或时序控制，并返回修改后的正向和负向条件数据。

## 输入参数

| 参数名称 | 数据类型 | 必填 | 取值范围 | 描述 |
|----------|-----------|------|----------|------|
| `新正面条件` | CONDITIONING | 是 | - | 待修改的正向条件输入 |
| `新负面条件` | CONDITIONING | 是 | - | 待修改的负向条件输入 |
| `强度` | FLOAT | 是 | 0.0 至 10.0 | 应用于条件数据的强度乘数（默认值：1.0） |
| `设置条件区域` | STRING | 是 | "default"<br>"mask bounds" | 决定条件区域的计算方式 |
| `遮罩` | MASK | 否 | - | 用于约束条件区域的可选遮罩 |
| `约束` | HOOKS | 否 | - | 用于高级条件修改的可选钩子组 |
| `间隔` | TIMESTEPS_RANGE | 否 | - | 用于限制条件应用时间的可选时间步范围 |

## 输出结果

| 输出名称 | 数据类型 | 描述 |
|----------|-----------|------|
| `负面条件` | CONDITIONING | 应用属性修改后的正向条件数据 |
| `negative` | CONDITIONING | 应用属性修改后的负向条件数据 |
