> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/MinimaxTextToVideoNode/zh.md)

基于提示文本和可选参数，使用 MiniMax 的 API 同步生成视频。该节点通过连接 MiniMax 的文生视频服务，将文本描述转换为视频内容。

## 输入参数

| 参数名 | 数据类型 | 必填 | 取值范围 | 描述 |
|-----------|-----------|----------|-------|-------------|
| `prompt_text` | STRING | 是 | - | 用于指导视频生成的文本提示 |
| `model` | COMBO | 否 | "T2V-01"<br>"T2V-01-Director" | 用于视频生成的模型（默认："T2V-01"） |
| `seed` | INT | 否 | 0 到 18446744073709551615 | 用于创建噪声的随机种子（默认：0） |

## 输出参数

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `output` | VIDEO | 基于输入提示生成的视频 |
