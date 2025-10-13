> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/PairConditioningCombine/zh.md)

PairConditioningCombine 节点将两对条件数据（正面和负面）合并为单个条件对。该节点接收两个独立的条件对作为输入，并使用 ComfyUI 的内部条件组合逻辑进行合并。此节点为实验性功能，主要用于高级条件处理工作流。

## 输入参数

| 参数名 | 数据类型 | 必填 | 取值范围 | 描述 |
|-----------|-----------|----------|-------|-------------|
| `正面条件_A` | CONDITIONING | 是 | - | 第一个正面条件输入 |
| `负面条件_A` | CONDITIONING | 是 | - | 第一个负面条件输入 |
| `正面条件_B` | CONDITIONING | 是 | - | 第二个正面条件输入 |
| `负面条件_B` | CONDITIONING | 是 | - | 第二个负面条件输入 |

## 输出结果

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `负面条件` | CONDITIONING | 合并后的正面条件输出 |
| `negative` | CONDITIONING | 合并后的负面条件输出 |
