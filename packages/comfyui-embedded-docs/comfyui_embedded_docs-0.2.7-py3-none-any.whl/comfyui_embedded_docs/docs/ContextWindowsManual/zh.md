> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/ContextWindowsManual/zh.md)

Context Windows (Manual) 节点允许您在采样过程中手动配置模型的上下文窗口。它通过创建具有指定长度、重叠度和调度模式的重叠上下文片段，将数据处理为可管理的块，同时保持片段之间的连续性。

## 输入参数

| 参数名 | 数据类型 | 必需 | 取值范围 | 描述 |
|-----------|-----------|----------|-------|-------------|
| `model` | MODEL | 是 | - | 在采样过程中应用上下文窗口的模型。 |
| `context_length` | INT | 否 | 1+ | 上下文窗口的长度（默认值：16）。 |
| `context_overlap` | INT | 否 | 0+ | 上下文窗口的重叠度（默认值：4）。 |
| `context_schedule` | COMBO | 否 | `STATIC_STANDARD`<br>`UNIFORM_STANDARD`<br>`UNIFORM_LOOPED`<br>`BATCHED` | 上下文窗口的步进调度模式。 |
| `context_stride` | INT | 否 | 1+ | 上下文窗口的步长；仅适用于均匀调度模式（默认值：1）。 |
| `closed_loop` | BOOLEAN | 否 | - | 是否闭合上下文窗口循环；仅适用于循环调度模式（默认值：False）。 |
| `fuse_method` | COMBO | 否 | `PYRAMID`<br>`LIST_STATIC` | 用于融合上下文窗口的方法（默认值：PYRAMID）。 |
| `dim` | INT | 否 | 0-5 | 应用上下文窗口的维度（默认值：0）。 |

**参数约束条件：**

- `context_stride` 仅在选择了均匀调度模式时使用
- `closed_loop` 仅适用于循环调度模式
- `dim` 必须在 0 到 5 之间（包含边界值）

## 输出参数

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `model` | MODEL | 在采样过程中应用了上下文窗口的模型。 |
