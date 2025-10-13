> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/TripoRetargetNode/zh.md)

> 本文档由 AI 生成，如果您发现任何错误或有改进建议，请随时贡献！[在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/TripoRetargetNode/en.md)

TripoRetargetNode 通过重新定向运动数据，将预定义的动画应用到 3D 角色模型上。该节点接收一个先前处理过的 3D 模型，并应用多个预设动画之一，生成一个动画化的 3D 模型文件作为输出。该节点通过与 Tripo API 通信来处理动画重定向操作。

## 输入参数

| 参数 | 数据类型 | 必需 | 取值范围 | 描述 |
|-----------|-----------|----------|-------|-------------|
| `original_model_task_id` | RIG_TASK_ID | 是 | - | 要应用动画的先前处理过的 3D 模型的任务 ID |
| `animation` | STRING | 是 | "preset:idle"<br>"preset:walk"<br>"preset:climb"<br>"preset:jump"<br>"preset:slash"<br>"preset:shoot"<br>"preset:hurt"<br>"preset:fall"<br>"preset:turn" | 要应用到 3D 模型上的动画预设 |
| `auth_token` | AUTH_TOKEN_COMFY_ORG | 否 | - | 用于访问 Comfy.org API 的认证令牌 |
| `comfy_api_key` | API_KEY_COMFY_ORG | 否 | - | 用于访问 Comfy.org 服务的 API 密钥 |
| `unique_id` | UNIQUE_ID | 否 | - | 用于跟踪操作的唯一标识符 |

## 输出结果

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `model_file` | STRING | 生成的动画化 3D 模型文件 |
| `retarget task_id` | RETARGET_TASK_ID | 用于跟踪重定向操作的任务 ID |
