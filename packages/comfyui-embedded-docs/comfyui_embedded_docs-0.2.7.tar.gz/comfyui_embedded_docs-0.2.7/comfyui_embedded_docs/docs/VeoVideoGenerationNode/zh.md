> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/VeoVideoGenerationNode/zh.md)

使用 Google 的 Veo API 从文本提示生成视频。此节点可以根据文本描述和可选的图像输入创建视频，并支持控制宽高比、时长等参数。

## 输入参数

| 参数 | 数据类型 | 必填 | 取值范围 | 描述 |
|-----------|-----------|----------|-------|-------------|
| `prompt` | STRING | 是 | - | 视频的文本描述（默认：空） |
| `aspect_ratio` | COMBO | 是 | "16:9"<br>"9:16" | 输出视频的宽高比（默认："16:9"） |
| `negative_prompt` | STRING | 否 | - | 负面文本提示，用于引导视频中应避免的内容（默认：空） |
| `duration_seconds` | INT | 否 | 5-8 | 输出视频的时长（单位：秒）（默认：5） |
| `enhance_prompt` | BOOLEAN | 否 | - | 是否使用 AI 辅助增强提示词（默认：True） |
| `person_generation` | COMBO | 否 | "ALLOW"<br>"BLOCK" | 是否允许在视频中生成人物（默认："ALLOW"） |
| `seed` | INT | 否 | 0-4294967295 | 视频生成的随机种子（0 表示随机）（默认：0） |
| `image` | IMAGE | 否 | - | 用于引导视频生成的可选参考图像 |
| `model` | COMBO | 否 | "veo-2.0-generate-001" | 用于视频生成的 Veo 2 模型（默认："veo-2.0-generate-001"） |

**注意：** `generate_audio` 参数仅适用于 Veo 3.0 模型，节点会根据所选模型自动处理该参数。

## 输出结果

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `output` | VIDEO | 生成的视频文件 |
