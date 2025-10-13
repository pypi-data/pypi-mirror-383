> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/TripoTextToModelNode/zh.md)

使用 Tripo 的 API 根据文本提示同步生成 3D 模型。此节点接收文本描述并创建具有可选纹理和材质属性的 3D 模型。

## 输入参数

| 参数 | 数据类型 | 必需 | 范围 | 描述 |
|-----------|-----------|----------|-------|-------------|
| `prompt` | STRING | 是 | - | 用于生成 3D 模型的文本描述（多行输入） |
| `negative_prompt` | STRING | 否 | - | 描述生成模型中应避免内容的文本（多行输入） |
| `model_version` | COMBO | 否 | 多个可用选项 | 用于生成的 Tripo 模型版本 |
| `style` | COMBO | 否 | 多个可用选项 | 生成模型的风格设置（默认："None"） |
| `texture` | BOOLEAN | 否 | - | 是否为模型生成纹理（默认：True） |
| `pbr` | BOOLEAN | 否 | - | 是否生成 PBR（基于物理的渲染）材质（默认：True） |
| `image_seed` | INT | 否 | - | 图像生成的随机种子（默认：42） |
| `model_seed` | INT | 否 | - | 模型生成的随机种子（默认：42） |
| `texture_seed` | INT | 否 | - | 纹理生成的随机种子（默认：42） |
| `texture_quality` | COMBO | 否 | "standard"<br>"detailed" | 纹理生成的质量级别（默认："standard"） |
| `face_limit` | INT | 否 | -1 到 500000 | 生成模型中的最大面数，-1 表示无限制（默认：-1） |
| `quad` | BOOLEAN | 否 | - | 是否生成基于四边形的几何体而非三角形（默认：False） |

**注意：** `prompt` 参数是必需的，不能为空。如果未提供提示，节点将引发错误。

## 输出结果

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `model_file` | STRING | 生成的 3D 模型文件 |
| `model task_id` | MODEL_TASK_ID | 模型生成过程的唯一任务标识符 |
