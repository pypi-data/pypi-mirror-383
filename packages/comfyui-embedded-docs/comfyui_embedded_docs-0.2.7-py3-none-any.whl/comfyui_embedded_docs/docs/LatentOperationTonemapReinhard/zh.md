> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/LatentOperationTonemapReinhard/zh.md)

> 本文档由 AI 生成。如果您发现任何错误或有改进建议，请随时贡献！[在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/LatentOperationTonemapReinhard/en.md)

LatentOperationTonemapReinhard 节点对潜在向量应用 Reinhard 色调映射技术。该方法通过基于均值和标准差的统计方法对潜在向量进行归一化处理，并调整其幅度，处理强度由乘数参数控制。

## 输入参数

| 参数名 | 数据类型 | 必填 | 取值范围 | 描述 |
|-----------|-----------|----------|-------|-------------|
| `乘数` | FLOAT | 否 | 0.0 至 100.0 | 控制色调映射效果的强度（默认值：1.0） |

## 输出结果

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `operation` | LATENT_OPERATION | 返回可应用于潜在向量的色调映射操作 |
