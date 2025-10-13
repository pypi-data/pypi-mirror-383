> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/RecraftVectorizeImageNode/zh.md)

> 本文档由 AI 生成。如果您发现任何错误或有改进建议，请随时贡献！[在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/RecraftVectorizeImageNode/en.md)

从输入图像同步生成 SVG。该节点通过处理输入批次中的每个图像并将结果组合成单个 SVG 输出来将栅格图像转换为矢量图形格式。

## 输入参数

| 参数名 | 数据类型 | 必填 | 取值范围 | 描述 |
|-----------|-----------|----------|-------|-------------|
| `图像` | IMAGE | 是 | - | 要转换为 SVG 格式的输入图像 |
| `auth_token` | AUTH_TOKEN_COMFY_ORG | 否 | - | API 访问的认证令牌 |
| `comfy_api_key` | API_KEY_COMFY_ORG | 否 | - | Comfy.org 服务的 API 密钥 |

## 输出参数

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `SVG` | SVG | 生成的矢量图形输出，包含所有处理后的图像结果 |
