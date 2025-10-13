> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/RecordAudio/zh.md)

> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！[在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/RecordAudio/en.md)

RecordAudio 节点加载通过音频录制界面录制或选择的音频文件。它处理音频文件并将其转换为波形格式，可供工作流中的其他音频处理节点使用。该节点会自动检测采样率并准备音频数据以供进一步处理。

## 输入参数

| 参数 | 数据类型 | 必填 | 取值范围 | 描述 |
|-----------|-----------|----------|-------|-------------|
| `audio` | AUDIO_RECORD | 是 | N/A | 来自音频录制界面的音频录制输入 |

## 输出参数

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `AUDIO` | AUDIO | 包含波形和采样率信息的已处理音频数据 |
