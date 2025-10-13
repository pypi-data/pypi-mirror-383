> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/ModelSamplingContinuousV/zh.md)

ModelSamplingContinuousV 节点通过应用连续 V-prediction 采样参数来修改模型的采样行为。它会创建输入模型的克隆副本，并使用自定义的 sigma 范围设置进行配置，实现高级采样控制。这允许用户通过特定的最小和最大 sigma 值来微调采样过程。

## 输入参数

| 参数 | 数据类型 | 必需 | 取值范围 | 描述 |
|------|-----------|------|----------|------|
| `模型` | MODEL | 是 | - | 要应用连续 V-prediction 采样进行修改的输入模型 |
| `采样` | STRING | 是 | "v_prediction" | 要应用的采样方法（当前仅支持 V-prediction） |
| `最大西格玛` | FLOAT | 是 | 0.0 - 1000.0 | 采样的最大 sigma 值（默认：500.0） |
| `最小西格玛` | FLOAT | 是 | 0.0 - 1000.0 | 采样的最小 sigma 值（默认：0.03） |

## 输出结果

| 输出名称 | 数据类型 | 描述 |
|----------|-----------|------|
| `模型` | MODEL | 已应用连续 V-prediction 采样的修改后模型 |
