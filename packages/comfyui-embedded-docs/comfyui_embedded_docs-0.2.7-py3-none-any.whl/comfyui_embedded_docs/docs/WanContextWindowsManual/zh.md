> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/WanContextWindowsManual/zh.md)

WAN 上下文窗口（手动）节点允许您为类似 WAN 的二维处理模型手动配置上下文窗口。该节点通过在采样过程中指定窗口长度、重叠量、调度方法和融合技术，应用自定义的上下文窗口设置。这使您能够精确控制模型在不同上下文区域中处理信息的方式。

## 输入参数

| 参数名称 | 数据类型 | 必填 | 取值范围 | 描述 |
|-----------|-----------|----------|-------|-------------|
| `model` | MODEL | 是 | - | 在采样过程中要应用上下文窗口的模型。 |
| `context_length` | INT | 是 | 1 到 1048576 | 上下文窗口的长度（默认值：81）。 |
| `context_overlap` | INT | 是 | 0 到 1048576 | 上下文窗口的重叠量（默认值：30）。 |
| `context_schedule` | COMBO | 是 | "static_standard"<br>"uniform_standard"<br>"uniform_looped"<br>"batched" | 上下文窗口的调度策略。 |
| `context_stride` | INT | 是 | 1 到 1048576 | 上下文窗口的步长；仅适用于均匀调度（默认值：1）。 |
| `closed_loop` | BOOLEAN | 是 | - | 是否闭合上下文窗口循环；仅适用于循环调度（默认值：False）。 |
| `fuse_method` | COMBO | 是 | "pyramid" | 用于融合上下文窗口的方法（默认值："pyramid"）。 |

**注意：** `context_stride` 参数仅影响均匀调度，`closed_loop` 仅适用于循环调度。上下文长度和重叠值会在处理过程中自动调整以确保最小有效值。

## 输出参数

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `model` | MODEL | 应用了上下文窗口配置的模型。 |
