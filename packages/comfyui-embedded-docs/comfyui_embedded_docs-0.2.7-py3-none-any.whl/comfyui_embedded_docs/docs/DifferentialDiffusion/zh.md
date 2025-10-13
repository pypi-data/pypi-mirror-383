> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/DifferentialDiffusion/zh.md)

> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！[在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/DifferentialDiffusion/en.md)

Differential Diffusion 节点通过基于时间步阈值应用二值掩码来修改去噪过程。它会创建一个在原始去噪掩码和基于阈值的二值掩码之间进行混合的掩码，从而允许对扩散过程强度进行受控调整。

## 输入参数

| 参数 | 数据类型 | 必需 | 取值范围 | 描述 |
|-------|-----------|----------|-------|-------------|
| `模型` | MODEL | 是 | - | 要修改的扩散模型 |
| `strength` | FLOAT | 否 | 0.0 - 1.0 | 控制原始去噪掩码与二值阈值掩码之间的混合强度（默认值：1.0） |

## 输出结果

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `模型` | MODEL | 带有更新后去噪掩码函数的修改版扩散模型 |
