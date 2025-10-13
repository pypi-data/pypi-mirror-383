> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/ConditioningSetProperties/zh.md)

> 本文档由 AI 生成，如果您发现任何错误或有改进建议，请随时贡献！[在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/ConditioningSetProperties/en.md)

ConditioningSetProperties 节点通过调整强度、区域设置以及应用可选遮罩或时间步范围来修改条件数据的属性。它允许您通过设置特定参数来控制条件数据在图像生成过程中的应用方式，从而影响条件调节对生成过程的作用。

## 输入参数

| 参数名 | 数据类型 | 输入类型 | 默认值 | 取值范围 | 描述 |
|-----------|-----------|------------|---------|-------|-------------|
| `新条件` | CONDITIONING | 必填 | - | - | 要修改的条件数据 |
| `强度` | FLOAT | 必填 | 1.0 | 0.0-10.0 | 控制条件调节效果的强度 |
| `设置条件区域` | STRING | 必填 | default | ["default", "mask bounds"] | 决定条件区域的应用方式 |
| `遮罩` | MASK | 可选 | - | - | 用于限制条件调节应用区域的可选遮罩 |
| `约束` | HOOKS | 可选 | - | - | 用于自定义处理的可选钩子函数 |
| `间隔` | TIMESTEPS_RANGE | 可选 | - | - | 用于限制条件调节生效时间范围的可选时间步范围 |

**注意：** 当提供 `mask` 时，`set_cond_area` 参数可设置为 "mask bounds"，以将条件调节应用限制在遮罩区域内。

## 输出结果

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `CONDITIONING` | CONDITIONING | 具有更新属性的修改后条件数据 |
