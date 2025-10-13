> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/SamplingPercentToSigma/zh.md)

## 概述

SamplingPercentToSigma 节点使用模型的采样参数将采样百分比值转换为对应的 sigma 值。它接收一个介于 0.0 到 1.0 之间的百分比值，并将其映射到模型噪声调度中的适当 sigma 值，同时提供返回计算得到的 sigma 值或边界处的实际最大/最小 sigma 值的选项。

## 输入

| 参数 | 数据类型 | 必需 | 范围 | 描述 |
|-----------|-----------|----------|-------|-------------|
| `model` | MODEL | 是 | - | 包含用于转换的采样参数的模型 |
| `sampling_percent` | FLOAT | 是 | 0.0 到 1.0 | 要转换为 sigma 的采样百分比（默认：0.0） |
| `return_actual_sigma` | BOOLEAN | 是 | - | 返回实际的 sigma 值，而非用于区间检查的值。这仅影响 0.0 和 1.0 处的计算结果（默认：False） |

## 输出

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `sigma_value` | FLOAT | 与输入采样百分比对应的转换后的 sigma 值 |
