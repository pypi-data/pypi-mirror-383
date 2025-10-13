> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/WanAnimateToVideo/zh.md)

WanAnimateToVideo 节点通过结合包括姿态参考、面部表情和背景元素在内的多重条件输入来生成视频内容。它处理各种视频输入以创建连贯的动画序列，同时保持帧间的时间一致性。该节点处理潜在空间操作，并可通过延续运动模式来扩展现有视频。

## 输入参数

| 参数名称 | 数据类型 | 必填 | 取值范围 | 描述 |
|-----------|-----------|----------|-------|-------------|
| `positive` | CONDITIONING | 是 | - | 用于引导生成期望内容的正向条件输入 |
| `negative` | CONDITIONING | 是 | - | 用于避免生成不需要内容的负向条件输入 |
| `vae` | VAE | 是 | - | 用于编码和解码图像数据的 VAE 模型 |
| `width` | INT | 否 | 16 至 MAX_RESOLUTION | 输出视频宽度（像素）（默认：832，步长：16） |
| `height` | INT | 否 | 16 至 MAX_RESOLUTION | 输出视频高度（像素）（默认：480，步长：16） |
| `length` | INT | 否 | 1 至 MAX_RESOLUTION | 要生成的帧数（默认：77，步长：4） |
| `batch_size` | INT | 否 | 1 至 4096 | 同时生成的视频数量（默认：1） |
| `clip_vision_output` | CLIP_VISION_OUTPUT | 否 | - | 用于附加条件输入的 CLIP 视觉模型输出（可选） |
| `reference_image` | IMAGE | 否 | - | 用作生成起点的参考图像 |
| `face_video` | IMAGE | 否 | - | 提供面部表情指导的视频输入 |
| `pose_video` | IMAGE | 否 | - | 提供姿态和运动指导的视频输入 |
| `continue_motion_max_frames` | INT | 否 | 1 至 MAX_RESOLUTION | 从先前运动延续的最大帧数（默认：5，步长：4） |
| `background_video` | IMAGE | 否 | - | 与生成内容合成的背景视频 |
| `character_mask` | MASK | 否 | - | 定义选择性处理角色区域的蒙版 |
| `continue_motion` | IMAGE | 否 | - | 用于保持时间一致性的先前运动序列延续 |
| `video_frame_offset` | INT | 否 | 0 至 MAX_RESOLUTION | 在所有输入视频中跳过的帧数。用于分块生成长视频。连接到前一个节点的 video_frame_offset 输出以扩展视频。（默认：0，步长：1） |

**参数约束：**

- 当提供 `pose_video` 且 `trim_to_pose_video` 逻辑激活时，输出长度将调整为匹配姿态视频时长
- `face_video` 在处理时会自动调整为 512x512 分辨率
- `continue_motion` 帧数受 `continue_motion_max_frames` 参数限制
- 输入视频（`face_video`、`pose_video`、`background_video`、`character_mask`）在处理前会按 `video_frame_offset` 进行偏移
- 如果 `character_mask` 仅包含单帧，该帧将在所有帧中重复使用
- 当提供 `clip_vision_output` 时，它会同时应用于正向和负向条件输入

## 输出参数

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `positive` | CONDITIONING | 包含附加视频上下文的修改后正向条件输入 |
| `negative` | CONDITIONING | 包含附加视频上下文的修改后负向条件输入 |
| `latent` | LATENT | 潜在空间格式的生成视频内容 |
| `trim_latent` | INT | 用于下游处理的潜在空间修剪信息 |
| `trim_image` | INT | 参考运动帧的图像空间修剪信息 |
| `video_frame_offset` | INT | 用于分块继续视频生成的更新帧偏移量 |
