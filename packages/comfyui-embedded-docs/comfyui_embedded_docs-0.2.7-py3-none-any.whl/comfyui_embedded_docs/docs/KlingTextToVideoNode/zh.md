> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/KlingTextToVideoNode/zh.md)

Kling 文本转视频节点可将文本描述转换为视频内容。它接收文本提示并根据指定的配置设置生成相应的视频序列。该节点支持不同的宽高比和生成模式，可生成不同时长和质量的视频。

## 输入参数

| 参数名称 | 数据类型 | 必填 | 取值范围 | 描述 |
|-----------|-----------|----------|-------|-------------|
| `prompt` | STRING | 是 | - | 正向文本提示（默认：无） |
| `negative_prompt` | STRING | 是 | - | 负向文本提示（默认：无） |
| `cfg_scale` | FLOAT | 否 | 0.0-1.0 | 配置缩放值（默认：1.0） |
| `aspect_ratio` | COMBO | 否 | KlingVideoGenAspectRatio 中的选项 | 视频宽高比设置（默认："16:9"） |
| `mode` | COMBO | 否 | 提供多个选项 | 用于视频生成的配置，格式为：模式/时长/模型名称（默认：modes[4]） |

## 输出结果

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `video_id` | VIDEO | 生成的视频输出 |
| `duration` | STRING | 生成视频的唯一标识符 |
| `duration` | STRING | 生成视频的时长信息 |
