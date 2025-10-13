> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！[在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/AudioEncoderEncode/zh.md)

AudioEncoderEncode 节点通过使用音频编码器模型对音频数据进行编码处理。它接收音频输入并将其转换为编码表示，可在条件处理流程中用于进一步处理。该节点将原始音频波形转换为适合基于音频的机器学习应用的格式。

## 输入参数

| 参数 | 数据类型 | 输入类型 | 默认值 | 范围 | 描述 |
|-------|-----------|------------|---------|-------|-------------|
| `audio_encoder` | AUDIO_ENCODER | 必填 | - | - | 用于处理音频输入的音频编码器模型 |
| `audio` | AUDIO | 必填 | - | - | 包含波形和采样率信息的音频数据 |

## 输出参数

| 输出名称 | 数据类型 | 描述 |
|-----------|-----------|-------------|
| `output` | AUDIO_ENCODER_OUTPUT | 由音频编码器生成的编码音频表示 |
