> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/SkipLayerGuidanceDiTSimple/zh.md)

SkipLayerGuidanceDiT 节点的简化版本，仅在去噪过程中修改无条件传递。该节点通过根据指定的时序和层参数，在无条件传递期间选择性跳过特定层，从而对 DiT（扩散变换器）模型中的特定变换器层应用跳跃层引导。

## 输入参数

| 参数名 | 数据类型 | 必填 | 取值范围 | 描述 |
|-----------|-----------|----------|-------|-------------|
| `model` | MODEL | 是 | - | 要应用跳跃层引导的模型 |
| `double_layers` | STRING | 是 | - | 要跳过的双块层索引的逗号分隔列表（默认："7, 8, 9"） |
| `single_layers` | STRING | 是 | - | 要跳过的单块层索引的逗号分隔列表（默认："7, 8, 9"） |
| `start_percent` | FLOAT | 是 | 0.0 - 1.0 | 跳跃层引导开始的去噪过程起始百分比（默认：0.0） |
| `end_percent` | FLOAT | 是 | 0.0 - 1.0 | 跳跃层引导停止的去噪过程结束百分比（默认：1.0） |

**注意：** 仅当 `double_layers` 和 `single_layers` 都包含有效层索引时才会应用跳跃层引导。如果两者均为空，节点将返回未修改的原始模型。

## 输出结果

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `model` | MODEL | 已对指定层应用跳跃层引导的修改后模型 |
