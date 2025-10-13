> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/DiffusersLoader/zh.md)

DiffusersLoader 节点从 diffusers 格式加载预训练模型。它会搜索包含 model_index.json 文件的有效 diffusers 模型目录，并将其加载为 MODEL、CLIP 和 VAE 组件以供流程使用。此节点属于已弃用的加载器类别，提供与 Hugging Face diffusers 模型的兼容性。

## 输入参数

| 参数 | 数据类型 | 必需 | 取值范围 | 描述 |
|-----------|-----------|----------|-------|-------------|
| `模型路径` | STRING | 是 | 提供多个选项<br>（自动从 diffusers 文件夹填充） | 要加载的 diffusers 模型目录路径。该节点会自动扫描配置的 diffusers 文件夹中的有效 diffusers 模型，并列出可用选项。 |

## 输出结果

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `MODEL` | MODEL | 从 diffusers 格式加载的模型组件 |
| `CLIP` | CLIP | 从 diffusers 格式加载的 CLIP 模型组件 |
| `VAE` | VAE | 从 diffusers 格式加载的 VAE（变分自编码器）组件 |
