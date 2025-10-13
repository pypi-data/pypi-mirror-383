> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/TripoRigNode/zh.md)

## 概述

TripoRigNode 通过原始模型任务 ID 生成带骨骼绑定的 3D 模型。该节点会向 Tripo API 发送请求，使用 Tripo 规范创建 GLB 格式的动画骨骼绑定，然后持续轮询 API 直到骨骼绑定生成任务完成。

## 输入

| 参数名 | 数据类型 | 必填 | 取值范围 | 描述 |
|-----------|-----------|----------|-------|-------------|
| `original_model_task_id` | MODEL_TASK_ID | 是 | - | 待绑定骨骼的原始 3D 模型的任务 ID |
| `auth_token` | AUTH_TOKEN_COMFY_ORG | 否 | - | 用于访问 Comfy.org API 的认证令牌 |
| `comfy_api_key` | API_KEY_COMFY_ORG | 否 | - | 用于 Comfy.org 服务认证的 API 密钥 |
| `unique_id` | UNIQUE_ID | 否 | - | 用于跟踪操作的唯一标识符 |

## 输出

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `model_file` | STRING | 生成的带骨骼绑定的 3D 模型文件 |
| `rig task_id` | RIG_TASK_ID | 用于跟踪骨骼绑定生成过程的任务 ID |
