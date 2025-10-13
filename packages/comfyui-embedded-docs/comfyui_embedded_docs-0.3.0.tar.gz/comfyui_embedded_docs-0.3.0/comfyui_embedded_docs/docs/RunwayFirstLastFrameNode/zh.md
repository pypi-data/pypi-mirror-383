> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/RunwayFirstLastFrameNode/zh.md)

Runway 首尾帧转视频节点通过上传首尾关键帧和文本提示来生成视频。它使用 Runway 的 Gen-3 模型在提供的起始帧和结束帧之间创建平滑过渡。这对于结束帧与起始帧差异较大的复杂过渡特别有用。

## 输入参数

| 参数名 | 数据类型 | 必填 | 取值范围 | 描述 |
|-----------|-----------|----------|-------|-------------|
| `prompt` | STRING | 是 | 无 | 用于生成的文本提示（默认：空字符串） |
| `start_frame` | IMAGE | 是 | 无 | 用于视频的起始帧 |
| `end_frame` | IMAGE | 是 | 无 | 用于视频的结束帧。仅支持 gen3a_turbo 模型 |
| `duration` | COMBO | 是 | 多个可用选项 | 从可用的时长选项中选择视频时长 |
| `ratio` | COMBO | 是 | 多个可用选项 | 从可用的 RunwayGen3aAspectRatio 选项中选择宽高比 |
| `seed` | INT | 否 | 0-4294967295 | 用于生成的随机种子（默认：0） |

**参数约束：**

- `prompt` 必须包含至少 1 个字符
- `start_frame` 和 `end_frame` 的最大尺寸必须为 7999x7999 像素
- `start_frame` 和 `end_frame` 的宽高比必须在 0.5 到 2.0 之间
- `end_frame` 参数仅在使用 gen3a_turbo 模型时受支持

## 输出参数

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `output` | VIDEO | 在起始帧和结束帧之间过渡生成的视频 |
