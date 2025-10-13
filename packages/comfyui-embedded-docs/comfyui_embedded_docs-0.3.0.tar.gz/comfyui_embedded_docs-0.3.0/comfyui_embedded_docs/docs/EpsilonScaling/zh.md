> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](<https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/Epsilon> Scaling/zh.md)

> 本文档由 AI 生成。如果您发现任何错误或有改进建议，请随时贡献！[在 GitHub 上编辑](<https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/Epsilon> Scaling/en.md)

实现了研究论文《阐明扩散模型中的曝光偏差》中的 Epsilon Scaling 方法。该方法通过在采样过程中缩放预测噪声来改善样本质量。它使用统一的调度策略来减轻扩散模型中的曝光偏差。

## 输入参数

| 参数名 | 数据类型 | 必填 | 取值范围 | 描述 |
|-----------|-----------|----------|-------|-------------|
| `model` | MODEL | 是 | - | 要应用 epsilon scaling 的模型 |
| `scaling_factor` | FLOAT | 否 | 0.5 - 1.5 | 用于缩放预测噪声的因子（默认值：1.005） |

## 输出结果

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `model` | MODEL | 应用了 epsilon scaling 的模型 |
