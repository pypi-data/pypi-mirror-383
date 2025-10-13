> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/SetHookKeyframes/zh.md)

> 本文档由 AI 生成。如果您发现任何错误或有改进建议，请随时贡献！[在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/SetHookKeyframes/en.md)

Set Hook Keyframes 节点允许您对现有的钩子组应用关键帧调度功能。它接收一个钩子组，并可选择性地应用关键帧时间信息来控制不同钩子在生成过程中的执行时机。当提供关键帧时，该节点会克隆钩子组并为组内的所有钩子设置关键帧时间。

## 输入参数

| 参数 | 数据类型 | 必填 | 取值范围 | 描述 |
|------|-----------|------|----------|------|
| `约束` | HOOKS | 是 | - | 将要应用关键帧调度的钩子组 |
| `约束关键帧` | HOOK_KEYFRAMES | 否 | - | 包含钩子执行时间信息的可选关键帧组 |

## 输出结果

| 输出名称 | 数据类型 | 描述 |
|----------|-----------|------|
| `约束` | HOOKS | 应用了关键帧调度的修改后钩子组（如果提供了关键帧则会克隆） |
