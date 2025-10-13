> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/CreateHookModelAsLoraModelOnly/zh.md)

此节点创建一个钩子，用于应用 LoRA（低秩适应）模型来仅修改神经网络的模型组件。它会加载一个检查点文件，并以指定的强度应用于模型，同时保持 CLIP 组件不变。这是一个实验性节点，扩展了基础 CreateHookModelAsLora 类的功能。

## 输入参数

| 参数名 | 数据类型 | 必填 | 取值范围 | 描述 |
|-----------|-----------|----------|-------|-------------|
| `Checkpoint名称` | STRING | 是 | 提供多个选项 | 要作为 LoRA 模型加载的检查点文件。可用选项取决于 checkpoints 文件夹中的内容。 |
| `模型强度` | FLOAT | 是 | -20.0 至 20.0 | 将 LoRA 应用于模型组件的强度乘数（默认值：1.0） |
| `前一个约束` | HOOKS | 否 | - | 可选的先前钩子，用于与此钩子链接 |

## 输出结果

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `hooks` | HOOKS | 创建的钩子组，包含 LoRA 模型修改 |
