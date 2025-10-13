> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/RunwayImageToVideoNodeGen4/zh.md)

Runway Image to Video (Gen4 Turbo) 节点使用 Runway 的 Gen4 Turbo 模型，从单个起始帧生成视频。它接收文本提示和初始图像帧，然后根据提供的持续时间和宽高比设置创建视频序列。该节点负责将起始帧上传到 Runway 的 API 并返回生成的视频。

## 输入参数

| 参数 | 数据类型 | 必需 | 取值范围 | 描述 |
|-----------|-----------|----------|-------|-------------|
| `prompt` | STRING | 是 | - | 用于生成的文本提示（默认：空字符串） |
| `start_frame` | IMAGE | 是 | - | 用于视频的起始帧 |
| `duration` | COMBO | 是 | 多个可用选项 | 从可用持续时间选项中选择视频时长 |
| `ratio` | COMBO | 是 | 多个可用选项 | 从可用的 Gen4 Turbo 宽高比选项中选择画面比例 |
| `seed` | INT | 否 | 0 到 4294967295 | 用于生成的随机种子（默认：0） |

**参数约束：**

- `start_frame` 图像的尺寸不得超过 7999x7999 像素
- `start_frame` 图像的宽高比必须在 0.5 到 2.0 之间
- `prompt` 必须至少包含一个字符

## 输出参数

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `output` | VIDEO | 基于输入帧和提示生成的视频 |
