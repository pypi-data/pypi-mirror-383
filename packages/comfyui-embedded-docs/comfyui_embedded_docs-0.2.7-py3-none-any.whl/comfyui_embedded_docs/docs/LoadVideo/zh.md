> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/LoadVideo/zh.md)

> 本文档由 AI 生成。如果您发现任何错误或有改进建议，请随时贡献！[在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/LoadVideo/en.md)

Load Video 节点从输入目录加载视频文件，使其可在工作流中进行处理。它从指定的输入文件夹读取视频文件，并将其输出为可连接到其他视频处理节点的视频数据。

## 输入参数

| 参数 | 数据类型 | 必需 | 取值范围 | 描述 |
|------|-----------|------|----------|------|
| `文件` | STRING | 是 | 提供多个选项 | 要从输入目录加载的视频文件 |

**注意：** `file` 参数的可用选项会根据输入目录中存在的视频文件动态生成。仅显示支持内容类型的视频文件。

## 输出结果

| 输出名称 | 数据类型 | 描述 |
|----------|-----------|------|
| `video` | VIDEO | 已加载的视频数据，可传递给其他视频处理节点 |
