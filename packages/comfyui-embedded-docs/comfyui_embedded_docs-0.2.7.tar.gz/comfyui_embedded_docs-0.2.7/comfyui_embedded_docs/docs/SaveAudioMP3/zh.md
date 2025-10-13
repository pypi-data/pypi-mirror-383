> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/SaveAudioMP3/zh.md)

# SaveAudioMP3

SaveAudioMP3 节点将音频数据保存为 MP3 文件。它接收音频输入，并将其导出到指定的输出目录，支持自定义文件名和质量设置。该节点自动处理文件命名和格式转换，以创建可播放的 MP3 文件。

## 输入参数

| 参数 | 数据类型 | 必需 | 取值范围 | 描述 |
|------|-----------|------|----------|-------------|
| `audio` | AUDIO | 是 | - | 要保存为 MP3 文件的音频数据 |
| `filename_prefix` | STRING | 否 | - | 输出文件名的前缀（默认："audio/ComfyUI"） |
| `quality` | STRING | 否 | "V0"<br>"128k"<br>"320k" | MP3 文件的音频质量设置（默认："V0"） |
| `prompt` | PROMPT | 否 | - | 内部提示数据（由系统自动提供） |
| `extra_pnginfo` | EXTRA_PNGINFO | 否 | - | 额外的 PNG 信息（由系统自动提供） |

## 输出结果

| 输出名称 | 数据类型 | 描述 |
|----------|-----------|-------------|
| *无* | - | 此节点不返回任何输出数据，但会将音频文件保存到输出目录 |
