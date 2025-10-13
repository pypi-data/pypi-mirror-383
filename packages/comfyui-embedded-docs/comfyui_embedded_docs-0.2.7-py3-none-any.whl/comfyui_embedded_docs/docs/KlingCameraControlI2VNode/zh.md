> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/KlingCameraControlI2VNode/zh.md)

# Kling 图像转视频相机控制节点

Kling 图像转视频相机控制节点能够将静态图像转换为具有专业相机运镜效果的电影级视频。这个专业的图像转视频节点允许您控制虚拟相机动作，包括缩放、旋转、平移、倾斜和第一人称视角，同时保持对原始图像的聚焦。相机控制目前仅在专业模式下支持，使用 kling-v1-5 模型，时长为 5 秒。

## 输入参数

| 参数 | 数据类型 | 必需 | 范围 | 描述 |
|-----------|-----------|----------|-------|-------------|
| `start_frame` | IMAGE | 是 | - | 参考图像 - URL 或 Base64 编码字符串，不能超过 10MB，分辨率不低于 300*300px，宽高比在 1:2.5 ~ 2.5:1 之间。Base64 不应包含 data:image 前缀。 |
| `prompt` | STRING | 是 | - | 正向文本提示词 |
| `negative_prompt` | STRING | 是 | - | 负向文本提示词 |
| `cfg_scale` | FLOAT | 否 | 0.0-1.0 | 控制文本引导的强度（默认：0.75） |
| `aspect_ratio` | COMBO | 否 | 多个选项可用 | 视频宽高比选择（默认：16:9） |
| `camera_control` | CAMERA_CONTROL | 是 | - | 可使用 Kling 相机控制节点创建。控制视频生成过程中的相机移动和运动。 |

## 输出参数

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `video_id` | VIDEO | 生成的视频输出 |
| `duration` | STRING | 生成视频的唯一标识符 |
| `duration` | STRING | 生成视频的时长 |
