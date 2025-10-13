> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/ConditioningSetDefaultAndCombine/zh.md)

## 概述

该节点使用基于钩子的系统将条件数据与默认条件数据相结合。它接收一个主要条件输入和一个默认条件输入，然后根据指定的钩子配置将它们合并。最终输出一个融合了两种来源的单一条件数据。

## 输入

| 参数 | 数据类型 | 输入类型 | 默认值 | 范围 | 描述 |
|-----------|-----------|------------|---------|-------|-------------|
| `cond` | CONDITIONING | 必填 | - | - | 待处理的主要条件输入 |
| `cond_DEFAULT` | CONDITIONING | 必填 | - | - | 将与主要条件数据合并的默认条件数据 |
| `hooks` | HOOKS | 可选 | - | - | 控制条件数据处理和合并方式的可选钩子配置 |

## 输出

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `CONDITIONING` | CONDITIONING | 合并主要和默认条件输入后得到的组合条件数据 |
