> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/KlingImage2VideoNode/zh.md)

Kling Image to Video 节点能够基于起始图像，通过文本提示生成视频内容。该节点接收参考图像，并根据提供的正向和负向文本描述创建视频序列，同时提供多种配置选项用于模型选择、时长和宽高比。

## 输入参数

| 参数名称 | 数据类型 | 是否必填 | 取值范围 | 参数说明 |
|----------|----------|----------|----------|----------|
| `start_frame` | IMAGE | 是 | - | 用于生成视频的参考图像。 |
| `prompt` | STRING | 是 | - | 正向文本提示。 |
| `negative_prompt` | STRING | 是 | - | 负向文本提示。 |
| `model_name` | COMBO | 是 | 提供多个选项 | 视频生成模型选择（默认："kling-v2-master"）。 |
| `cfg_scale` | FLOAT | 是 | 0.0-1.0 | 配置缩放参数（默认：0.8）。 |
| `mode` | COMBO | 是 | 提供多个选项 | 视频生成模式选择（默认：std）。 |
| `aspect_ratio` | COMBO | 是 | 提供多个选项 | 生成视频的宽高比（默认：field_16_9）。 |
| `duration` | COMBO | 是 | 提供多个选项 | 生成视频的时长（默认：field_5）。 |

## 输出结果

| 输出名称 | 数据类型 | 输出说明 |
|----------|----------|----------|
| `video_id` | VIDEO | 生成的视频输出。 |
| `duration` | STRING | 生成视频的唯一标识符。 |
| `duration` | STRING | 生成视频的时长信息。 |
