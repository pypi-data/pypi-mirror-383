> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/ConditioningSetPropertiesAndCombine/zh.md)

# ConditioningSetPropertiesAndCombine 节点

ConditioningSetPropertiesAndCombine 节点通过将新条件输入中的属性应用到现有条件输入来修改条件数据。它结合了两个条件集，同时控制新条件的强度并指定条件区域的应用方式。

## 输入参数

| 参数 | 数据类型 | 输入类型 | 默认值 | 范围 | 描述 |
|-----------|-----------|------------|---------|-------|-------------|
| `条件` | CONDITIONING | 必填 | - | - | 待修改的原始条件数据 |
| `新条件` | CONDITIONING | 必填 | - | - | 提供要应用属性的新条件数据 |
| `强度` | FLOAT | 必填 | 1.0 | 0.0 - 10.0 | 控制新条件属性的强度 |
| `设置条件区域` | STRING | 必填 | default | ["default", "mask bounds"] | 决定条件区域的应用方式 |
| `遮罩` | MASK | 可选 | - | - | 用于定义特定条件区域的可选遮罩 |
| `约束` | HOOKS | 可选 | - | - | 用于自定义处理的可选钩子函数 |
| `间隔` | TIMESTEPS_RANGE | 可选 | - | - | 用于控制条件应用时机的可选时间步范围 |

**注意：** 当提供 `mask` 时，`set_cond_area` 参数可以使用 "mask bounds" 将条件应用限制在遮罩区域内。

## 输出结果

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `CONDITIONING` | CONDITIONING | 具有修改后属性的组合条件数据 |
