> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献您的力量！[在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/AudioEncoderLoader/zh.md)

AudioEncoderLoader 节点从您可用的音频编码器文件中加载音频编码器模型。它接收音频编码器文件名作为输入，并返回一个已加载的音频编码器模型，该模型可在工作流中用于音频处理任务。

## 输入参数

| 参数名 | 数据类型 | 输入类型 | 默认值 | 取值范围 | 描述 |
|--------|----------|----------|---------|----------|------|
| `audio_encoder_name` | STRING | COMBO | - | 可用的音频编码器文件 | 选择要从 audio_encoders 文件夹加载的音频编码器模型文件 |

## 输出参数

| 输出名称 | 数据类型 | 描述 |
|----------|----------|------|
| `audio_encoder` | AUDIO_ENCODER | 返回已加载的音频编码器模型，用于音频处理工作流 |
