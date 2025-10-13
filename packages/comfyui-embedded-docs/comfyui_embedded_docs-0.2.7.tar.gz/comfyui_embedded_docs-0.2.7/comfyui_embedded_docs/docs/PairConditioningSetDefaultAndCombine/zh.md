> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/PairConditioningSetDefaultAndCombine/zh.md)

## 概述

PairConditioningSetDefaultAndCombine 节点用于设置默认的条件化数值并将其与输入的条件化数据相结合。该节点接收正向和负向条件化输入及其对应的默认值，然后通过 ComfyUI 的钩子系统进行处理，最终生成包含默认值的条件化输出结果。

## 输入

| 参数 | 数据类型 | 必填 | 取值范围 | 描述 |
|------|-----------|------|----------|------|
| `positive` | CONDITIONING | 是 | - | 待处理的主正向条件化输入 |
| `negative` | CONDITIONING | 是 | - | 待处理的主负向条件化输入 |
| `positive_DEFAULT` | CONDITIONING | 是 | - | 作为备用值的默认正向条件化数据 |
| `negative_DEFAULT` | CONDITIONING | 是 | - | 作为备用值的默认负向条件化数据 |
| `hooks` | HOOKS | 否 | - | 用于自定义处理逻辑的可选钩子组 |

## 输出

| 输出名称 | 数据类型 | 描述 |
|----------|-----------|------|
| `positive` | CONDITIONING | 已处理并包含默认值的正向条件化数据 |
| `negative` | CONDITIONING | 已处理并包含默认值的负向条件化数据 |
