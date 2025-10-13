> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/TripoTextureNode/zh.md)

TripoTextureNode 使用 Tripo API 生成带纹理的 3D 模型。它接收模型任务 ID，并通过包括 PBR 材质、纹理质量设置和对齐方法在内的多种选项应用纹理生成功能。该节点通过与 Tripo API 通信来处理纹理生成请求，并返回生成的模型文件和任务 ID。

## 输入参数

| 参数 | 数据类型 | 必需 | 取值范围 | 描述 |
|-----------|-----------|----------|-------|-------------|
| `model_task_id` | MODEL_TASK_ID | 是 | - | 要应用纹理的模型任务 ID |
| `texture` | BOOLEAN | 否 | - | 是否生成纹理（默认值：True） |
| `pbr` | BOOLEAN | 否 | - | 是否生成 PBR（基于物理的渲染）材质（默认值：True） |
| `texture_seed` | INT | 否 | - | 纹理生成的随机种子（默认值：42） |
| `texture_quality` | COMBO | 否 | "standard"<br>"detailed" | 纹理生成的质量级别（默认值："standard"） |
| `texture_alignment` | COMBO | 否 | "original_image"<br>"geometry" | 纹理对齐方法（默认值："original_image"） |

*注意：此节点需要认证令牌和 API 密钥，这些由系统自动处理。*

## 输出参数

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `model_file` | STRING | 应用纹理后生成的模型文件 |
| `model task_id` | MODEL_TASK_ID | 用于跟踪纹理生成过程的任务 ID |
