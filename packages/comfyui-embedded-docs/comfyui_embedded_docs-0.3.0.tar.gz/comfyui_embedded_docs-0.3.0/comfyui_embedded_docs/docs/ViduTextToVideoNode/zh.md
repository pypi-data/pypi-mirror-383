> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/ViduTextToVideoNode/zh.md)

Vidu 文本转视频生成节点能够根据文本描述创建视频。它使用多种视频生成模型，将您的文本提示转换为视频内容，并提供可自定义的时长、宽高比和视觉风格设置。

## 输入参数

| 参数名称 | 数据类型 | 必填 | 取值范围 | 描述 |
|-----------|-----------|----------|-------|-------------|
| `model` | COMBO | 是 | `vidu_q1`<br>*其他 VideoModelName 选项* | 模型名称（默认值：vidu_q1） |
| `prompt` | STRING | 是 | - | 用于视频生成的文本描述 |
| `duration` | INT | 否 | 5-5 | 输出视频的时长（单位：秒）（默认值：5） |
| `seed` | INT | 否 | 0-2147483647 | 视频生成的随机种子（0 表示随机）（默认值：0） |
| `aspect_ratio` | COMBO | 否 | `r_16_9`<br>*其他 AspectRatio 选项* | 输出视频的宽高比（默认值：r_16_9） |
| `resolution` | COMBO | 否 | `r_1080p`<br>*其他 Resolution 选项* | 支持的数值可能因模型和时长而异（默认值：r_1080p） |
| `movement_amplitude` | COMBO | 否 | `auto`<br>*其他 MovementAmplitude 选项* | 画面中物体的运动幅度（默认值：auto） |

**注意：** `prompt` 字段为必填项且不能为空。`duration` 参数当前固定为 5 秒。

## 输出参数

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `output` | VIDEO | 基于文本提示生成的视频 |
