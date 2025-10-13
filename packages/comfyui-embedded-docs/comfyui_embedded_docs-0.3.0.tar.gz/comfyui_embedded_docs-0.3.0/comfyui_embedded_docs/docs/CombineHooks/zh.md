> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/CombineHooks/zh.md)

> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！[在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/CombineHooks/en.md)

Combine Hooks [2] 节点将两个钩子组合并为一个组合钩子组。它接收两个可选的钩子输入，并使用 ComfyUI 的钩子组合功能将它们合并。这使您可以整合多个钩子配置以实现流线型处理。

## 输入参数

| 参数 | 数据类型 | 输入类型 | 默认值 | 范围 | 描述 |
|------|-----------|------------|---------|-------|-------------|
| `hooks_A` | HOOKS | 可选 | 无 | - | 要合并的第一个钩子组 |
| `hooks_B` | HOOKS | 可选 | 无 | - | 要合并的第二个钩子组 |

**注意：** 两个输入都是可选的，但必须至少提供一个钩子组才能使节点正常工作。如果只提供一个钩子组，它将原样返回。

## 输出结果

| 输出名称 | 数据类型 | 描述 |
|----------|-----------|-------------|
| `hooks` | HOOKS | 包含两个输入组中所有钩子的组合钩子组 |
