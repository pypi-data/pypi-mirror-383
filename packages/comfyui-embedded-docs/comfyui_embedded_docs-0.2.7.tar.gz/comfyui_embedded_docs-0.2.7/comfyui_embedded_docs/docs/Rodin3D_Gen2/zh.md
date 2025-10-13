> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/Rodin3D_Gen2/zh.md)

Rodin3D_Gen2 节点使用 Rodin API 生成 3D 资源。它接收输入图像并将其转换为具有不同材质类型和多边形数量的 3D 模型。该节点自动处理整个生成过程，包括任务创建、状态轮询和文件下载。

## 输入参数

| 参数名 | 数据类型 | 必需 | 取值范围 | 描述 |
|-----------|-----------|----------|-------|-------------|
| `Images` | IMAGE | 是 | - | 用于 3D 模型生成的输入图像 |
| `Seed` | INT | 否 | 0-65535 | 生成用的随机种子值（默认：0） |
| `Material_Type` | COMBO | 否 | "PBR"<br>"Shaded" | 应用于 3D 模型的材质类型（默认："PBR"） |
| `Polygon_count` | COMBO | 否 | "4K-Quad"<br>"8K-Quad"<br>"18K-Quad"<br>"50K-Quad"<br>"2K-Triangle"<br>"20K-Triangle"<br>"150K-Triangle"<br>"500K-Triangle" | 生成 3D 模型的目标多边形数量（默认："500K-Triangle"） |
| `TAPose` | BOOLEAN | 否 | - | 是否应用 TAPose 处理（默认：False） |

## 输出结果

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `3D Model Path` | STRING | 生成的 3D 模型文件路径 |
