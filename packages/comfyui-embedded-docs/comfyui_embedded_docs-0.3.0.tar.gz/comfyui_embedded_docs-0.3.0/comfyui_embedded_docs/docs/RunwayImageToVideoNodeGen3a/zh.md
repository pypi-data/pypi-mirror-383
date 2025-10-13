> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/RunwayImageToVideoNodeGen3a/zh.md)

Runway Image to Video (Gen3a Turbo) 节点使用 Runway 的 Gen3a Turbo 模型从单个起始帧生成视频。它接收文本提示和初始图像帧，然后根据指定的持续时间和宽高比创建视频序列。此节点通过连接 Runway 的 API 进行远程生成处理。

## 输入参数

| 参数名 | 数据类型 | 必填 | 取值范围 | 描述 |
|-----------|-----------|----------|-------|-------------|
| `prompt` | STRING | 是 | 无 | 用于生成的文本提示（默认：""） |
| `start_frame` | IMAGE | 是 | 无 | 用于视频生成的起始帧 |
| `duration` | COMBO | 是 | 多个可用选项 | 从可用选项中选择视频时长 |
| `ratio` | COMBO | 是 | 多个可用选项 | 从可用选项中选择宽高比 |
| `seed` | INT | 否 | 0-4294967295 | 用于生成的随机种子（默认：0） |

**参数约束：**

- `start_frame` 的尺寸不得超过 7999x7999 像素
- `start_frame` 的宽高比必须在 0.5 到 2.0 之间
- `prompt` 必须包含至少一个字符（不能为空）

## 输出参数

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `output` | VIDEO | 生成的视频序列 |
