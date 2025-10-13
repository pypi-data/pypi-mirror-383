> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/ControlNetInpaintingAliMamaApply/zh.md)

ControlNetInpaintingAliMamaApply 节点通过将正向和负向条件与控制图像及蒙版相结合，为修复任务应用 ControlNet 条件处理。该节点会处理输入图像和蒙版，创建经过修改的条件来指导生成过程，从而实现对图像修复区域的精确控制。该节点支持强度调整和时序控制，可在生成过程的不同阶段微调 ControlNet 的影响程度。

## 输入参数

| 参数 | 数据类型 | 必需 | 取值范围 | 描述 |
|------|-----------|------|----------|------|
| `正面条件` | CONDITIONING | 是 | - | 引导生成朝向期望内容的正向条件 |
| `负面条件` | CONDITIONING | 是 | - | 引导生成远离不需要内容的负向条件 |
| `ControlNet` | CONTROL_NET | 是 | - | 提供对生成过程额外控制的 ControlNet 模型 |
| `vae` | VAE | 是 | - | 用于图像编码和解码的变分自编码器 |
| `图像` | IMAGE | 是 | - | 作为 ControlNet 控制引导的输入图像 |
| `遮罩` | MASK | 是 | - | 定义图像中哪些区域需要修复的蒙版 |
| `强度` | FLOAT | 是 | 0.0 到 10.0 | ControlNet 效果的强度（默认值：1.0） |
| `开始百分比` | FLOAT | 是 | 0.0 到 1.0 | ControlNet 影响在生成过程中开始的时间点（百分比）（默认值：0.0） |
| `结束百分比` | FLOAT | 是 | 0.0 到 1.0 | ControlNet 影响在生成过程中停止的时间点（百分比）（默认值：1.0） |

**注意：** 当 ControlNet 启用 `concat_mask` 时，蒙版会在处理前进行反转并应用到图像上，同时该蒙版会包含在发送给 ControlNet 的额外拼接数据中。

## 输出参数

| 输出名称 | 数据类型 | 描述 |
|----------|-----------|------|
| `负面条件` | CONDITIONING | 应用了 ControlNet 修复功能的修改后正向条件 |
| `负面条件` | CONDITIONING | 应用了 ControlNet 修复功能的修改后负向条件 |
