> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/SamplerSASolver/zh.md)

SamplerSASolver 节点为扩散模型实现了一种自定义采样算法。它采用预测器-校正器方法，通过可配置的阶数设置和随机微分方程（SDE）参数，从输入模型中生成样本。

## 输入参数

| 参数 | 数据类型 | 必填 | 取值范围 | 描述 |
|------|-----------|------|----------|------|
| `model` | MODEL | 是 | - | 用于采样的扩散模型 |
| `eta` | FLOAT | 是 | 0.0 - 10.0 | 控制步长缩放因子（默认值：1.0） |
| `sde_start_percent` | FLOAT | 是 | 0.0 - 1.0 | SDE 采样的起始百分比（默认值：0.2） |
| `sde_end_percent` | FLOAT | 是 | 0.0 - 1.0 | SDE 采样的结束百分比（默认值：0.8） |
| `s_noise` | FLOAT | 是 | 0.0 - 100.0 | 控制采样过程中添加的噪声量（默认值：1.0） |
| `predictor_order` | INT | 是 | 1 - 6 | 求解器中预测器组件的阶数（默认值：3） |
| `corrector_order` | INT | 是 | 0 - 6 | 求解器中校正器组件的阶数（默认值：4） |
| `use_pece` | BOOLEAN | 是 | - | 启用或禁用 PECE（预测-评估-校正-评估）方法 |
| `simple_order_2` | BOOLEAN | 是 | - | 启用或禁用简化的二阶计算 |

## 输出结果

| 输出名称 | 数据类型 | 描述 |
|----------|-----------|------|
| `sampler` | SAMPLER | 已配置的采样器对象，可用于扩散模型 |
