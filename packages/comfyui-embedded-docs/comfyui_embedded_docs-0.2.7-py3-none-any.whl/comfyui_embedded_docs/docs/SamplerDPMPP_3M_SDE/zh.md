> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/SamplerDPMPP_3M_SDE/zh.md)

SamplerDPMPP_3M_SDE 节点创建一个 DPM++ 3M SDE 采样器，用于采样过程。该采样器采用三阶多步随机微分方程方法，并具有可配置的噪声参数。该节点允许您选择在 GPU 或 CPU 上执行噪声计算。

## 输入参数

| 参数 | 数据类型 | 必填 | 取值范围 | 描述 |
|------|-----------|------|----------|------|
| `eta` | FLOAT | 是 | 0.0 - 100.0 | 控制采样过程的随机性（默认值：1.0） |
| `s_noise` | FLOAT | 是 | 0.0 - 100.0 | 控制采样过程中添加的噪声量（默认值：1.0） |
| `噪波设备` | COMBO | 是 | "gpu"<br>"cpu" | 选择噪声计算设备，可以是 GPU 或 CPU |

## 输出结果

| 输出名称 | 数据类型 | 描述 |
|----------|-----------|------|
| `sampler` | SAMPLER | 返回一个配置好的采样器对象，用于采样工作流 |
