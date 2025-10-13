> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/MinimaxSubjectToVideoNode/zh.md)

基于图像和提示词，以及可选参数，使用 MiniMax 的 API 同步生成视频。该节点通过主体图像和文本描述，利用 MiniMax 的视频生成服务创建视频。

## 输入参数

| 参数名 | 数据类型 | 必填 | 取值范围 | 描述 |
|-----------|-----------|----------|-------|-------------|
| `subject` | IMAGE | 是 | - | 用于视频生成参考的主体图像 |
| `prompt_text` | STRING | 是 | - | 指导视频生成的文本提示词（默认：空字符串） |
| `model` | COMBO | 否 | "S2V-01"<br> | 用于视频生成的模型（默认："S2V-01"） |
| `seed` | INT | 否 | 0 到 18446744073709551615 | 用于创建噪声的随机种子（默认：0） |

## 输出结果

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `output` | VIDEO | 基于输入主体图像和提示词生成的视频 |
