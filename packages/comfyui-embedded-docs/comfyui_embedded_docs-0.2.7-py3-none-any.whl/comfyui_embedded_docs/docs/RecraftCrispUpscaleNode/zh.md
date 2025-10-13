> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/RecraftCrispUpscaleNode/zh.md)

同步放大图像。使用"清晰放大"工具增强给定的栅格图像，提高图像分辨率，使图像更清晰、更干净。

## 输入参数

| 参数名 | 数据类型 | 必填 | 取值范围 | 描述 |
|-----------|-----------|----------|-------|-------------|
| `图像` | IMAGE | 是 | - | 需要放大的输入图像 |
| `auth_token` | STRING | 否 | - | Recraft API 的认证令牌 |
| `comfy_api_key` | STRING | 否 | - | Comfy.org 服务的 API 密钥 |

## 输出结果

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `图像` | IMAGE | 经过放大处理后的图像，具有更高的分辨率和清晰度 |
