> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/KlingStartEndFrameNode/zh.md)

# ## 概述

Kling 首尾帧转视频节点可创建一个在提供的起始图像和结束图像之间过渡的视频序列。它会生成中间所有帧，从而产生从第一帧到最后一帧的平滑转换。此节点调用图像转视频 API，但仅支持与 `image_tail` 请求字段配合使用的输入选项。

## ## 输入

| 参数 | 数据类型 | 必需 | 取值范围 | 描述 |
|------|-----------|------|----------|-------------|
| `start_frame` | IMAGE | 是 | - | 参考图像 - URL 或 Base64 编码字符串，不能超过 10MB，分辨率不低于 300*300 像素，宽高比在 1:2.5 ~ 2.5:1 之间。Base64 不应包含 data:image 前缀。 |
| `end_frame` | IMAGE | 是 | - | 参考图像 - 结束帧控制。URL 或 Base64 编码字符串，不能超过 10MB，分辨率不低于 300*300 像素。Base64 不应包含 data:image 前缀。 |
| `prompt` | STRING | 是 | - | 正向文本提示词 |
| `negative_prompt` | STRING | 是 | - | 负向文本提示词 |
| `cfg_scale` | FLOAT | 否 | 0.0-1.0 | 控制提示词引导的强度（默认值：0.5） |
| `aspect_ratio` | COMBO | 否 | "16:9"<br>"9:16"<br>"1:1"<br>"21:9"<br>"9:21"<br>"3:4"<br>"4:3" | 生成视频的宽高比（默认值："16:9"） |
| `mode` | COMBO | 否 | 提供多个选项 | 用于视频生成的配置，遵循格式：模式 / 时长 / 模型名称。（默认值：可用模式中的第三个选项） |

**图像约束条件：**

- 必须同时提供 `start_frame` 和 `end_frame`，且文件大小不能超过 10MB
- 最小分辨率：两张图像均为 300×300 像素
- `start_frame` 的宽高比必须在 1:2.5 和 2.5:1 之间
- Base64 编码的图像不应包含 "data:image" 前缀

## ## 输出

| 输出名称 | 数据类型 | 描述 |
|----------|-----------|-------------|
| `output` | VIDEO | 生成的视频序列 |
| `video_id` | STRING | 生成视频的唯一标识符 |
| `duration` | STRING | 生成视频的时长 |
