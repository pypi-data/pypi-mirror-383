> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/LatentApplyOperation/zh.md)

> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！[在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/LatentApplyOperation/en.md)

LatentApplyOperation 节点对潜在样本应用指定操作。它接收潜在数据和操作作为输入，使用提供的操作处理潜在样本，并返回修改后的潜在数据。该节点允许您在工作流中转换或操作潜在表示。

## 输入参数

| 参数 | 数据类型 | 必需 | 取值范围 | 描述 |
|-----------|-----------|----------|-------|-------------|
| `Latent` | LATENT | 是 | - | 需要通过操作处理的潜在样本 |
| `操作` | LATENT_OPERATION | 是 | - | 要应用于潜在样本的操作 |

## 输出结果

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `output` | LATENT | 应用操作后修改的潜在样本 |
