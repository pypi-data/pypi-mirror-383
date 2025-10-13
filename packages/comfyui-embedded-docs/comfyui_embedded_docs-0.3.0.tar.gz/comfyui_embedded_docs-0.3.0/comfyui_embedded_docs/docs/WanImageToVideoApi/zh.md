> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/WanImageToVideoApi/zh.md)

万图生视频节点从单个输入图像和文本提示开始生成视频内容。它通过根据提供的描述扩展初始帧来创建视频序列，并提供控制视频质量、时长和音频集成的选项。

## 输入参数

| 参数 | 数据类型 | 必需 | 取值范围 | 描述 |
|-----------|-----------|----------|-------|-------------|
| `model` | COMBO | 是 | "wan2.5-i2v-preview"<br>"wan2.5-i2v-preview" | 使用的模型（默认："wan2.5-i2v-preview"） |
| `image` | IMAGE | 是 | - | 输入图像，作为视频生成的第一帧 |
| `prompt` | STRING | 是 | - | 用于描述元素和视觉特征的提示词，支持英文/中文（默认：空） |
| `negative_prompt` | STRING | 否 | - | 负面文本提示词，用于指导避免生成的内容（默认：空） |
| `resolution` | COMBO | 否 | "480P"<br>"720P"<br>"1080P" | 视频分辨率质量（默认："480P"） |
| `duration` | INT | 否 | 5-10 | 可用时长：5秒和10秒（默认：5） |
| `audio` | AUDIO | 否 | - | 音频必须包含清晰、响亮的人声，无杂音和背景音乐 |
| `seed` | INT | 否 | 0-2147483647 | 生成使用的随机种子（默认：0） |
| `generate_audio` | BOOLEAN | 否 | - | 若无音频输入，是否自动生成音频（默认：False） |
| `prompt_extend` | BOOLEAN | 否 | - | 是否使用AI辅助增强提示词（默认：True） |
| `watermark` | BOOLEAN | 否 | - | 是否在结果中添加"AI生成"水印（默认：True） |

**约束条件：**

- 视频生成需要且仅需要一个输入图像
- 时长参数仅接受5或10秒的值
- 当提供音频时，音频时长必须在3.0到29.0秒之间

## 输出结果

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `output` | VIDEO | 基于输入图像和提示词生成的视频 |
