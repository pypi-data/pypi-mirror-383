> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/PikaStartEndFrameNode2_2/zh.md)

PikaFrames v2.2 节点通过组合您的首帧和尾帧来生成视频。您上传两张图像来定义起始点和结束点，AI 会在它们之间创建平滑过渡，从而生成完整的视频。

## 输入参数

| 参数名称 | 数据类型 | 是否必需 | 取值范围 | 描述 |
|-----------|-----------|----------|-------|-------------|
| `image_start` | IMAGE | 是 | - | 要组合的首帧图像。 |
| `image_end` | IMAGE | 是 | - | 要组合的尾帧图像。 |
| `prompt_text` | STRING | 是 | - | 描述期望视频内容的文本提示。 |
| `negative_prompt` | STRING | 是 | - | 描述视频中应避免内容的文本。 |
| `seed` | INT | 是 | - | 用于保持生成一致性的随机种子值。 |
| `resolution` | STRING | 是 | - | 输出视频分辨率。 |
| `duration` | INT | 是 | - | 生成视频的持续时间。 |

## 输出结果

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `output` | VIDEO | 通过 AI 过渡将起始帧和结束帧组合后生成的视频。 |
