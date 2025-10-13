> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/StabilityUpscaleFastNode/zh.md)

通过调用 Stability API 快速将图像放大至原始尺寸的 4 倍。此节点专门用于通过将低质量或压缩图像发送至 Stability AI 的快速放大服务来实现图像放大。

## 输入参数

| 参数名称 | 数据类型 | 是否必填 | 取值范围 | 功能说明 |
|-----------|-----------|----------|-------|-------------|
| `图像` | IMAGE | 是 | - | 待放大的输入图像 |

## 输出结果

| 输出名称 | 数据类型 | 功能说明 |
|-------------|-----------|-------------|
| `output` | IMAGE | 从 Stability AI API 返回的放大后图像 |
