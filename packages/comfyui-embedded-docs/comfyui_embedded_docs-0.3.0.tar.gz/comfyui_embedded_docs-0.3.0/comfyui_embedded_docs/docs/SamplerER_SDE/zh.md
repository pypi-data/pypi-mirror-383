> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/SamplerER_SDE/zh.md)

SamplerER_SDE 节点为扩散模型提供专门的采样方法，提供不同的求解器类型，包括 ER-SDE、逆时 SDE 和 ODE 方法。它允许控制采样过程的随机行为和计算阶段。该节点会根据所选求解器类型自动调整参数以确保正常功能。

## 输入参数

| 参数 | 数据类型 | 必需 | 取值范围 | 描述 |
|-----------|-----------|----------|-------|-------------|
| `solver_type` | COMBO | 是 | "ER-SDE"<br>"Reverse-time SDE"<br>"ODE" | 用于采样的求解器类型。决定扩散过程的数学方法。 |
| `max_stage` | INT | 是 | 1-3 | 采样过程的最大阶段数（默认：3）。控制计算复杂度和质量。 |
| `eta` | FLOAT | 是 | 0.0-100.0 | 逆时 SDE 的随机强度（默认：1.0）。当 eta=0 时，简化为确定性 ODE。此设置不适用于 ER-SDE 求解器类型。 |
| `s_noise` | FLOAT | 是 | 0.0-100.0 | 采样过程的噪声缩放因子（默认：1.0）。控制采样过程中应用的噪声量。 |

**参数约束：**

- 当 `solver_type` 设置为 "ODE" 或使用 "Reverse-time SDE" 且 `eta`=0 时，无论用户输入值如何，`eta` 和 `s_noise` 都会自动设置为 0。
- `eta` 参数仅影响 "Reverse-time SDE" 求解器类型，对 "ER-SDE" 求解器类型没有影响。

## 输出参数

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `sampler` | SAMPLER | 配置好的采样器对象，可在采样流水线中使用，具有指定的求解器设置。 |
