> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/RandomNoise/zh.md)

> 本文档由 AI 生成。如果您发现任何错误或有改进建议，请随时贡献！[在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/RandomNoise/en.md)

RandomNoise 节点基于种子值生成随机噪声模式。它创建可重现的噪声，可用于各种图像处理和生成任务。相同的种子将始终产生相同的噪声模式，从而确保多次运行结果的一致性。

## 输入参数

| 参数 | 数据类型 | 必需 | 取值范围 | 描述 |
|-----------|-----------|----------|-------|-------------|
| `噪波随机种` | INT | 是 | 0 到 18446744073709551615 | 用于生成随机噪声模式的种子值（默认值：0）。相同的种子将始终产生相同的噪声输出。 |

## 输出结果

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `noise` | NOISE | 基于提供的种子值生成的随机噪声模式。 |
