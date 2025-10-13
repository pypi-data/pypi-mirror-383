> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/RecraftRemoveBackgroundNode/zh.md)

此节点使用 Recraft API 服务从图像中移除背景。它会处理输入批次中的每张图像，并返回带有透明背景的处理后图像以及指示被移除背景区域的对应 Alpha 蒙版。

## 输入参数

| 参数名 | 数据类型 | 必填 | 取值范围 | 描述 |
|-----------|-----------|----------|-------|-------------|
| `图像` | IMAGE | 是 | - | 需要进行背景移除处理的输入图像 |
| `auth_token` | STRING | 否 | - | 用于访问 Recraft API 的身份验证令牌 |
| `comfy_api_key` | STRING | 否 | - | 用于 Comfy.org 服务集成的 API 密钥 |

## 输出结果

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `图像` | IMAGE | 处理后带有透明背景的图像 |
| `mask` | MASK | 指示被移除背景区域的 Alpha 通道蒙版 |
