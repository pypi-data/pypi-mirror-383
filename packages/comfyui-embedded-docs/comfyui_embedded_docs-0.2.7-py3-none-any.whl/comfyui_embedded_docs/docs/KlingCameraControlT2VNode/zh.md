> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/KlingCameraControlT2VNode/zh.md)

# ## 概述

Kling 文生视频相机控制节点可将文本转换为具有专业相机运动的电影级视频，模拟真实世界的电影摄影效果。此节点支持控制虚拟相机动作，包括缩放、旋转、平移、倾斜和第一人称视角，同时保持对原始文本的关注。由于相机控制仅在专业模式下支持，使用 kling-v1-5 模型且时长为 5 秒，因此持续时间、模式和模型名称已硬编码。

# ## 输入

| 参数 | 数据类型 | 必填 | 取值范围 | 描述 |
|------|-----------|------|----------|-------------|
| `prompt` | STRING | 是 | - | 正向文本提示词 |
| `negative_prompt` | STRING | 是 | - | 负向文本提示词 |
| `cfg_scale` | FLOAT | 否 | 0.0-1.0 | 控制输出与提示词的贴合程度（默认值：0.75） |
| `aspect_ratio` | COMBO | 否 | "16:9"<br>"9:16"<br>"1:1"<br>"21:9"<br>"3:4"<br>"4:3" | 生成视频的宽高比（默认值："16:9"） |
| `camera_control` | CAMERA_CONTROL | 否 | - | 可使用 Kling 相机控制节点创建。控制视频生成过程中的相机移动和运动效果。 |

# ## 输出

| 输出名称 | 数据类型 | 描述 |
|----------|-----------|-------------|
| `output` | VIDEO | 带有相机控制效果的生成视频 |
| `video_id` | STRING | 生成视频的唯一标识符 |
| `duration` | STRING | 生成视频的时长 |
