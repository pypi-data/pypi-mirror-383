> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/CheckpointLoader/zh.md)

> 本文档由 AI 生成。如果您发现任何错误或有改进建议，请随时贡献！[在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/CheckpointLoader/en.md)

CheckpointLoader 节点加载预训练的模型检查点及其配置文件。它接收配置文件和检查点文件作为输入，并返回已加载的模型组件，包括主模型、CLIP 模型和 VAE 模型，以供工作流使用。

## 输入参数

| 参数 | 数据类型 | 输入类型 | 默认值 | 取值范围 | 描述 |
|-------|-----------|------------|---------|-------|-------------|
| `配置名称` | STRING | 下拉选择 | - | 可用的配置文件 | 定义模型架构和设置的配置文件 |
| `Checkpoint名称` | STRING | 下拉选择 | - | 可用的检查点文件 | 包含训练好的模型权重和参数的检查点文件 |

**注意：** 此节点需要同时选择配置文件和检查点文件。配置文件必须与要加载的检查点文件的架构匹配。

## 输出参数

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `MODEL` | MODEL | 已加载的主模型组件，准备进行推理 |
| `CLIP` | CLIP | 已加载的 CLIP 模型组件，用于文本编码 |
| `VAE` | VAE | 已加载的 VAE 模型组件，用于图像编码和解码 |

**重要提示：** 此节点已被标记为弃用，可能在未来的版本中被移除。对于新的工作流，请考虑使用替代的加载节点。
