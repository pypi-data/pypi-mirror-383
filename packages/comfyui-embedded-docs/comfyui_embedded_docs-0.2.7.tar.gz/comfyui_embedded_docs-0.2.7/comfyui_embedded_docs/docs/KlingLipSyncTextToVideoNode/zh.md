> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/KlingLipSyncTextToVideoNode/zh.md)

Kling 唇形同步文本转视频节点可将视频文件中的嘴部运动与文本提示进行同步。该节点接收输入视频并生成一个新视频，其中角色的唇部运动与提供的文本内容保持一致。该节点利用语音合成技术创建自然逼真的语音同步效果。

## 输入参数

| 参数 | 数据类型 | 必填 | 取值范围 | 描述 |
|-----------|-----------|----------|-------|-------------|
| `视频` | VIDEO | 是 | - | 用于唇形同步的输入视频文件 |
| `文本` | STRING | 是 | - | 唇形同步视频生成的文本内容。在模式为 text2video 时必需。最大长度为 120 个字符。 |
| `语音` | COMBO | 否 | "Melody"<br>"Bella"<br>"Aria"<br>"Ethan"<br>"Ryan"<br>"Dorothy"<br>"Nathan"<br>"Lily"<br>"Aaron"<br>"Emma"<br>"Grace"<br>"Henry"<br>"Isabella"<br>"James"<br>"Katherine"<br>"Liam"<br>"Mia"<br>"Noah"<br>"Olivia"<br>"Sophia" | 唇形同步音频的语音选择（默认："Melody"） |
| `语速` | FLOAT | 否 | 0.8-2.0 | 语速。有效范围：0.8~2.0，精确到小数点后一位（默认：1） |

**视频要求：**

- 视频文件大小不应超过 100MB
- 高度/宽度应在 720px 至 1920px 之间
- 时长应在 2 秒至 10 秒之间

## 输出参数

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `视频ID` | VIDEO | 生成的带唇形同步音频的视频 |
| `时长` | STRING | 生成视频的唯一标识符 |
| `duration` | STRING | 生成视频的时长信息 |
