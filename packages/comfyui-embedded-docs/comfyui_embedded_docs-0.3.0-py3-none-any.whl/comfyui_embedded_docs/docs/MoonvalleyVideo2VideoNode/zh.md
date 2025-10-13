> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/MoonvalleyVideo2VideoNode/zh.md)

Moonvalley Marey 视频到视频节点能够根据文本描述将输入视频转换为新的视频。它利用 Moonvalley API 生成与您的提示词匹配的视频，同时保留原始视频的运动或姿态特征。您可以通过文本提示词和各种生成参数来控制输出视频的风格和内容。

## 输入参数

| 参数 | 数据类型 | 必需 | 取值范围 | 描述 |
|-----------|-----------|----------|-------|-------------|
| `prompt` | STRING | 是 | - | 描述要生成的视频内容（支持多行输入） |
| `negative_prompt` | STRING | 否 | - | 负面提示文本（默认：包含大量负面描述符的列表） |
| `seed` | INT | 是 | 0-4294967295 | 随机种子值（默认：9） |
| `video` | VIDEO | 是 | - | 用于生成输出视频的参考视频。视频长度必须至少为5秒，超过5秒的视频将被自动裁剪。仅支持 MP4 格式。 |
| `control_type` | COMBO | 否 | "Motion Transfer"<br>"Pose Transfer" | 控制类型选择（默认："Motion Transfer"） |
| `motion_intensity` | INT | 否 | 0-100 | 仅在 control_type 为 'Motion Transfer' 时使用（默认：100） |
| `steps` | INT | 是 | 1-100 | 推理步数（默认：33） |

**注意：** `motion_intensity` 参数仅在 `control_type` 设置为 "Motion Transfer" 时生效。当使用 "Pose Transfer" 时，此参数将被忽略。

## 输出参数

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `output` | VIDEO | 生成的视频输出 |
