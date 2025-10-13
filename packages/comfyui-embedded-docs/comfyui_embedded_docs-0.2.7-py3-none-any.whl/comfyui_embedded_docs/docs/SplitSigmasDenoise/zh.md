> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/SplitSigmasDenoise/zh.md)

SplitSigmasDenoise 节点根据去噪强度参数将一系列 sigma 值划分为两部分。它将输入的 sigma 序列分割为高 sigma 序列和低 sigma 序列，分割点由总步数乘以去噪因子确定。这样可以将噪声调度分离到不同的强度范围，以便进行专门处理。

## 输入参数

| 参数 | 数据类型 | 必需 | 取值范围 | 描述 |
|-----------|-----------|----------|-------|-------------|
| `Sigmas` | SIGMAS | 是 | - | 表示噪声调度的输入 sigma 值序列 |
| `降噪` | FLOAT | 是 | 0.0 - 1.0 | 决定 sigma 序列分割点的去噪强度因子（默认值：1.0） |

## 输出结果

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `低方差` | SIGMAS | 包含较高 sigma 值的 sigma 序列前半部分 |
| `low_sigmas` | SIGMAS | 包含较低 sigma 值的 sigma 序列后半部分 |
