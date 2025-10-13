> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/PreviewAudio/zh.md)

PreviewAudio 节点生成临时音频预览文件，可在界面中显示。它继承自 SaveAudio 节点，但会将文件保存至临时目录并使用随机文件名前缀。这使用户能够快速预览音频输出而无需创建永久文件。

## 输入参数

| 参数名 | 数据类型 | 必填 | 取值范围 | 描述 |
|-----------|-----------|----------|-------|-------------|
| `音频` | AUDIO | 是 | - | 需要预览的音频数据 |
| `prompt` | PROMPT | 否 | - | 内部使用的隐藏参数 |
| `extra_pnginfo` | EXTRA_PNGINFO | 否 | - | 内部使用的隐藏参数 |

## 输出结果

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `ui` | UI | 在界面中显示音频预览 |
