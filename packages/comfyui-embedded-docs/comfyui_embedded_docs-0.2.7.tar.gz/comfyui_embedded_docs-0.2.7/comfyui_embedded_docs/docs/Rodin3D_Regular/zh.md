> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/Rodin3D_Regular/zh.md)

Rodin 3D Regular 节点通过 Rodin API 生成 3D 资源。该节点接收输入图像并通过 Rodin 服务进行处理以创建 3D 模型。该节点处理从任务创建到下载最终 3D 模型文件的完整工作流程。

## 输入参数

| 参数名 | 数据类型 | 必需 | 取值范围 | 描述 |
|-----------|-----------|----------|-------|-------------|
| `Images` | IMAGE | 是 | - | 用于 3D 模型生成的输入图像 |
| `Seed` | INT | 是 | - | 用于可重现结果的随机种子值 |
| `Material_Type` | STRING | 是 | - | 应用于 3D 模型的材质类型 |
| `Polygon_count` | STRING | 是 | - | 生成 3D 模型的目标多边形数量 |

## 输出结果

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `3D Model Path` | STRING | 生成的 3D 模型文件路径 |
