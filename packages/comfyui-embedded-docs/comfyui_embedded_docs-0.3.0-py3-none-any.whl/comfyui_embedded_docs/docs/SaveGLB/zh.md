> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/SaveGLB/zh.md)

> 本文档由 AI 生成。如果您发现任何错误或有改进建议，请随时贡献！[在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/SaveGLB/en.md)

SaveGLB 节点将 3D 网格数据保存为 GLB 文件，这是一种常见的 3D 模型格式。它接收网格数据作为输入，并使用指定的文件名前缀将其导出到输出目录。如果输入包含多个网格对象，该节点可以保存多个网格，并且在启用元数据时会自动向文件添加元数据。

## 输入参数

| 参数 | 数据类型 | 必需 | 取值范围 | 描述 |
|-----------|-----------|----------|-------|-------------|
| `网格` | MESH | 是 | - | 要保存为 GLB 文件的 3D 网格数据 |
| `文件名前缀` | STRING | 否 | - | 输出文件名的前缀（默认："mesh/ComfyUI"） |

## 输出结果

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `ui` | UI | 在用户界面中显示保存的 GLB 文件，包含文件名和子文件夹信息 |
