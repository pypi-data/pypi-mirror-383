> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/KlingVideoExtendNode/zh.md)

Kling 视频扩展节点允许您扩展由其他 Kling 节点创建的视频。该节点通过视频 ID 识别现有视频，并根据您的文本提示生成额外内容。该节点的工作原理是将您的扩展请求发送到 Kling API，并返回扩展后的视频及其新的 ID 和时长。

## 输入参数

| 参数 | 数据类型 | 必填 | 取值范围 | 描述 |
|-----------|-----------|----------|-------|-------------|
| `prompt` | STRING | 否 | - | 用于指导视频扩展的正面文本提示 |
| `negative_prompt` | STRING | 否 | - | 用于避免在扩展视频中出现某些元素的负面文本提示 |
| `cfg_scale` | FLOAT | 否 | 0.0 - 1.0 | 控制提示引导的强度（默认值：0.5） |
| `video_id` | STRING | 是 | - | 要扩展的视频 ID。支持由文生视频、图生视频和先前视频扩展操作生成的视频。扩展后总时长不能超过 3 分钟。 |

**注意：** `video_id` 必须引用由其他 Kling 节点创建的视频，且扩展后的总时长不能超过 3 分钟。

## 输出结果

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `video_id` | VIDEO | 由 Kling API 生成的扩展视频 |
| `duration` | STRING | 扩展视频的唯一标识符 |
| `duration` | STRING | 扩展视频的时长 |
