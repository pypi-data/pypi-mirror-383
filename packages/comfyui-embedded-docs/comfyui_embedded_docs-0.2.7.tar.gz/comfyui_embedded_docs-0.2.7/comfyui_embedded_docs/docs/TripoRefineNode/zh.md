> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/TripoRefineNode/zh.md)

> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！[在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/TripoRefineNode/en.md)

TripoRefineNode 用于优化专门由 v1.4 版 Tripo 模型创建的 3D 模型草稿。它接收一个模型任务 ID，通过 Tripo API 进行处理，生成模型的改进版本。此节点专门设计用于处理由 Tripo v1.4 模型生成的草稿模型。

## 输入参数

| 参数名 | 数据类型 | 必填 | 取值范围 | 描述 |
|-----------|-----------|----------|-------|-------------|
| `model_task_id` | MODEL_TASK_ID | 是 | - | 必须是 v1.4 版 Tripo 模型 |
| `auth_token` | AUTH_TOKEN_COMFY_ORG | 否 | - | Comfy.org API 的认证令牌 |
| `comfy_api_key` | API_KEY_COMFY_ORG | 否 | - | Comfy.org 服务的 API 密钥 |
| `unique_id` | UNIQUE_ID | 否 | - | 操作的唯一标识符 |

**注意：** 此节点仅接受由 Tripo v1.4 模型创建的草稿模型。使用其他版本的模型可能会导致错误。

## 输出结果

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `model_file` | STRING | 优化后模型的文件路径或引用 |
| `model task_id` | MODEL_TASK_ID | 优化模型操作的任务标识符 |
