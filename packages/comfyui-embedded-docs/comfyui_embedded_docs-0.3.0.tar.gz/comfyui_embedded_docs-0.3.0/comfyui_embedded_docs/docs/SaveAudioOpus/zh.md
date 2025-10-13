> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/SaveAudioOpus/zh.md)

> 本文档由 AI 生成。如果您发现任何错误或有改进建议，请随时贡献！[在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/SaveAudioOpus/en.md)

SaveAudioOpus 节点将音频数据保存为 Opus 格式文件。它接收音频输入，并将其导出为具有可配置质量设置的压缩 Opus 文件。该节点自动处理文件命名，并将输出保存到指定的输出目录。

## 输入参数

| 参数 | 数据类型 | 必需 | 取值范围 | 描述 |
|------|-----------|------|----------|------|
| `audio` | AUDIO | 是 | - | 要保存为 Opus 文件的音频数据 |
| `filename_prefix` | STRING | 否 | - | 输出文件名的前缀（默认："audio/ComfyUI"） |
| `quality` | COMBO | 否 | "64k"<br>"96k"<br>"128k"<br>"192k"<br>"320k" | Opus 文件的音频质量设置（默认："128k"） |

## 输出结果

| 输出名称 | 数据类型 | 描述 |
|----------|-----------|------|
| - | - | 此节点不返回任何输出值。其主要功能是将音频文件保存到磁盘。 |
