> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/ModelSamplingAuraFlow/zh.md)

ModelSamplingAuraFlow 节点为扩散模型应用专门的采样配置，特别针对 AuraFlow 模型架构设计。该节点通过应用偏移参数来调整采样分布，从而修改模型的采样行为。此节点继承自 SD3 模型采样框架，并提供对采样过程的精细控制。

## 输入参数

| 参数 | 数据类型 | 必需 | 取值范围 | 描述 |
|-----------|-----------|----------|-------|-------------|
| `模型` | MODEL | 是 | - | 要应用 AuraFlow 采样配置的扩散模型 |
| `移位` | FLOAT | 是 | 0.0 - 100.0 | 应用于采样分布的偏移值（默认值：1.73） |

## 输出结果

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `模型` | MODEL | 已应用 AuraFlow 采样配置的修改后模型 |
