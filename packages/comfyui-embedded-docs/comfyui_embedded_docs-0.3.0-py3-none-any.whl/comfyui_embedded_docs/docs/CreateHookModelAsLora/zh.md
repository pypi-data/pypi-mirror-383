> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/CreateHookModelAsLora/zh.md)

> 本文档由 AI 生成，如果您发现任何错误或有改进建议，请随时贡献！[在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/CreateHookModelAsLora/en.md)

此节点通过加载检查点权重并对模型和 CLIP 组件应用强度调整，创建一个作为 LoRA（低秩自适应）的钩子模型。它允许您通过基于钩子的方法对现有模型应用 LoRA 风格的修改，实现微调和自适应而无需永久更改模型。该节点可以与之前的钩子组合使用，并缓存已加载的权重以提高效率。

## 输入参数

| 参数 | 数据类型 | 必需 | 范围 | 描述 |
|------|-----------|------|------|-------------|
| `Checkpoint名称` | COMBO | 是 | 多个可用选项 | 用于加载权重的检查点文件（从可用检查点中选择） |
| `模型强度` | FLOAT | 是 | -20.0 到 20.0 | 应用于模型权重的强度乘数（默认：1.0） |
| `CLIP强度` | FLOAT | 是 | -20.0 到 20.0 | 应用于 CLIP 权重的强度乘数（默认：1.0） |
| `前一个约束` | HOOKS | 否 | - | 可选的先前钩子，用于与新创建的 LoRA 钩子组合 |

**参数约束：**

- `ckpt_name` 参数从可用检查点文件夹加载检查点
- 两个强度参数接受从 -20.0 到 20.0 的值，步长为 0.01
- 当未提供 `prev_hooks` 时，节点会创建新的钩子组
- 节点会缓存已加载的权重，避免多次重新加载同一检查点

## 输出结果

| 输出名称 | 数据类型 | 描述 |
|----------|-----------|-------------|
| `HOOKS` | HOOKS | 创建的 LoRA 钩子，如果提供了先前钩子则会与之组合 |
