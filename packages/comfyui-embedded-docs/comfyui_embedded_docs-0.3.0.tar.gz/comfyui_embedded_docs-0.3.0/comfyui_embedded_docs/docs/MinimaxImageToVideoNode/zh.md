> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/MinimaxImageToVideoNode/zh.md)

基于输入图像和提示文本，以及可选参数，使用 MiniMax 的 API 同步生成视频。该节点接收输入图像和文本描述来创建视频序列，并提供多种模型选项和配置设置。

## 输入参数

| 参数 | 数据类型 | 必需 | 取值范围 | 描述 |
|-----------|-----------|----------|-------|-------------|
| `image` | IMAGE | 是 | - | 用作视频生成首帧的输入图像 |
| `prompt_text` | STRING | 是 | - | 指导视频生成的文本提示（默认值：空字符串） |
| `model` | COMBO | 是 | "I2V-01-Director"<br>"I2V-01"<br>"I2V-01-live" | 用于视频生成的模型（默认值："I2V-01"） |
| `seed` | INT | 否 | 0 到 18446744073709551615 | 用于创建噪声的随机种子（默认值：0） |

## 输出结果

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `output` | VIDEO | 生成的视频输出 |
