> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/CLIPAttentionMultiply/zh.md)

> 本文档由 AI 生成。如果您发现任何错误或有改进建议，请随时贡献！[在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/CLIPAttentionMultiply/en.md)

CLIPAttentionMultiply 节点允许您通过为自注意力层的不同组件应用乘法因子来调整 CLIP 模型中的注意力机制。它通过修改 CLIP 模型注意力机制中的查询、键、值和输出投影权重及偏置来实现。这个实验性节点会创建一个应用了指定缩放因子的输入 CLIP 模型的修改副本。

## 输入参数

| 参数 | 数据类型 | 输入类型 | 默认值 | 范围 | 描述 |
|-----------|-----------|------------|---------|-------|-------------|
| `clip` | CLIP | 必选 | - | - | 要修改的 CLIP 模型 |
| `q` | FLOAT | 必选 | 1.0 | 0.0 - 10.0 | 查询投影权重和偏置的乘法因子 |
| `k` | FLOAT | 必选 | 1.0 | 0.0 - 10.0 | 键投影权重和偏置的乘法因子 |
| `v` | FLOAT | 必选 | 1.0 | 0.0 - 10.0 | 值投影权重和偏置的乘法因子 |
| `输出` | FLOAT | 必选 | 1.0 | 0.0 - 10.0 | 输出投影权重和偏置的乘法因子 |

## 输出参数

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `CLIP` | CLIP | 返回应用了指定注意力缩放因子的修改后 CLIP 模型 |
