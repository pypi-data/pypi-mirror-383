> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/ByteDanceTextToVideoNode/zh.md)

字节跳动文生视频节点通过基于文本提示的 API 使用字节跳动模型生成视频。它接收文本描述和各种视频设置作为输入，然后创建符合所提供规格的视频。该节点负责处理 API 通信，并将生成的视频作为输出返回。

## 输入参数

| 参数名 | 数据类型 | 输入类型 | 默认值 | 取值范围 | 描述 |
|-----------|-----------|------------|---------|-------|-------------|
| `model` | STRING | 下拉选项 | seedance_1_pro | Text2VideoModelName 选项 | 模型名称 |
| `prompt` | STRING | 字符串 | - | - | 用于生成视频的文本提示。 |
| `resolution` | STRING | 下拉选项 | - | ["480p", "720p", "1080p"] | 输出视频的分辨率。 |
| `aspect_ratio` | STRING | 下拉选项 | - | ["16:9", "4:3", "1:1", "3:4", "9:16", "21:9"] | 输出视频的宽高比。 |
| `duration` | INT | 整数 | 5 | 3-12 | 输出视频的时长（单位：秒）。 |
| `seed` | INT | 整数 | 0 | 0-2147483647 | 用于生成的随机种子。（可选） |
| `camera_fixed` | BOOLEAN | 布尔值 | False | - | 指定是否固定摄像机。平台会在您的提示词后附加固定摄像机的指令，但不保证实际效果。（可选） |
| `watermark` | BOOLEAN | 布尔值 | True | - | 是否在视频上添加"AI生成"水印。（可选） |

**参数约束：**

- `prompt` 参数在去除空白字符后必须至少包含 1 个字符
- `prompt` 参数不能包含以下文本参数："resolution"、"ratio"、"duration"、"seed"、"camerafixed"、"watermark"
- `duration` 参数限制在 3 到 12 秒之间的值
- `seed` 参数接受 0 到 2,147,483,647 之间的值

## 输出参数

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `output` | VIDEO | 生成的视频文件 |
