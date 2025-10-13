> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/Veo3VideoGenerationNode/zh.md)

使用 Google 的 Veo 3 API 从文本提示生成视频。此节点支持两种 Veo 3 模型：veo-3.0-generate-001 和 veo-3.0-fast-generate-001。它扩展了基础 Veo 节点的功能，增加了 Veo 3 特有的特性，包括音频生成和固定的 8 秒时长。

## 输入参数

| 参数 | 数据类型 | 必需 | 范围 | 描述 |
|-----------|-----------|----------|-------|-------------|
| `prompt` | STRING | 是 | - | 视频的文本描述（默认：""） |
| `aspect_ratio` | COMBO | 是 | "16:9"<br>"9:16" | 输出视频的宽高比（默认："16:9"） |
| `negative_prompt` | STRING | 否 | - | 负面文本提示，用于引导视频中应避免的内容（默认：""） |
| `duration_seconds` | INT | 否 | 8-8 | 输出视频的时长（单位：秒）（Veo 3 仅支持 8 秒）（默认：8） |
| `enhance_prompt` | BOOLEAN | 否 | - | 是否使用 AI 辅助增强提示（默认：True） |
| `person_generation` | COMBO | 否 | "ALLOW"<br>"BLOCK" | 是否允许在视频中生成人物（默认："ALLOW"） |
| `seed` | INT | 否 | 0-4294967295 | 视频生成的随机种子（0 表示随机）（默认：0） |
| `image` | IMAGE | 否 | - | 用于引导视频生成的可选参考图像 |
| `model` | COMBO | 否 | "veo-3.0-generate-001"<br>"veo-3.0-fast-generate-001" | 用于视频生成的 Veo 3 模型（默认："veo-3.0-generate-001"） |
| `generate_audio` | BOOLEAN | 否 | - | 为视频生成音频。所有 Veo 3 模型均支持此功能。（默认：False） |

**注意：** 对于所有 Veo 3 模型，`duration_seconds` 参数固定为 8 秒且无法更改。

## 输出参数

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `output` | VIDEO | 生成的视频文件 |
