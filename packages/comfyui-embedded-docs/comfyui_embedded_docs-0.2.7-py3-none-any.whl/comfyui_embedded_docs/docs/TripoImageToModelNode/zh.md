> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/TripoImageToModelNode/zh.md)

使用 Tripo 的 API 基于单张图像同步生成 3D 模型。此节点接收输入图像，并将其转换为 3D 模型，提供纹理、质量和模型属性的多种自定义选项。

## 输入参数

| 参数 | 数据类型 | 必需 | 取值范围 | 描述 |
|-----------|-----------|----------|-------|-------------|
| `image` | IMAGE | 是 | - | 用于生成 3D 模型的输入图像 |
| `model_version` | COMBO | 否 | 提供多个选项 | 用于生成的 Tripo 模型版本 |
| `style` | COMBO | 否 | 提供多个选项 | 生成模型的风格设置（默认："None"） |
| `texture` | BOOLEAN | 否 | - | 是否为模型生成纹理（默认：True） |
| `pbr` | BOOLEAN | 否 | - | 是否使用基于物理的渲染（默认：True） |
| `model_seed` | INT | 否 | - | 模型生成的随机种子（默认：42） |
| `orientation` | COMBO | 否 | 提供多个选项 | 生成模型的方向设置 |
| `texture_seed` | INT | 否 | - | 纹理生成的随机种子（默认：42） |
| `texture_quality` | COMBO | 否 | "standard"<br>"detailed" | 纹理生成的质量级别（默认："standard"） |
| `texture_alignment` | COMBO | 否 | "original_image"<br>"geometry" | 纹理映射的对齐方法（默认："original_image"） |
| `face_limit` | INT | 否 | -1 到 500000 | 生成模型中的最大面数，-1 表示无限制（默认：-1） |
| `quad` | BOOLEAN | 否 | - | 是否使用四边形面而非三角形面（默认：False） |

**注意：** `image` 参数是必需的，必须提供才能使节点正常工作。如果未提供图像，节点将引发 RuntimeError。

## 输出参数

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `model_file` | STRING | 生成的 3D 模型文件 |
| `model task_id` | MODEL_TASK_ID | 用于跟踪模型生成过程的任务 ID |
