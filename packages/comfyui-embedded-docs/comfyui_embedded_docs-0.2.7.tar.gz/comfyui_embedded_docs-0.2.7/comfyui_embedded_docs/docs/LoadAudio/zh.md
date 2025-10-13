> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/LoadAudio/zh.md)

> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！[在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/LoadAudio/en.md)

LoadAudio 节点从输入目录加载音频文件，并将其转换为可供 ComfyUI 中其他音频节点处理的格式。该节点读取音频文件并提取波形数据和采样率，使其可用于下游音频处理任务。

## 输入参数

| 参数 | 数据类型 | 必需 | 取值范围 | 描述 |
|------|-----------|------|----------|------|
| `音频` | AUDIO | 是 | 输入目录中所有支持的音频/视频文件 | 要从输入目录加载的音频文件 |

**注意：** 该节点仅接受 ComfyUI 输入目录中存在的音频和视频文件。文件必须存在且可访问才能成功加载。

## 输出结果

| 输出名称 | 数据类型 | 描述 |
|----------|-----------|------|
| `AUDIO` | AUDIO | 包含波形和采样率信息的音频数据 |
