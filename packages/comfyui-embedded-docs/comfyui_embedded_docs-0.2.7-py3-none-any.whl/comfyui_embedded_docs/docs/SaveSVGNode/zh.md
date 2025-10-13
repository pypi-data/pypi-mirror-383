> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/SaveSVGNode/zh.md)

将 SVG 文件保存到磁盘。此节点接收 SVG 数据作为输入，并将其保存到您的输出目录，可选择嵌入元数据。该节点自动处理带计数器后缀的文件命名，并可将工作流提示信息直接嵌入 SVG 文件。

## 输入参数

| 参数 | 数据类型 | 必填 | 取值范围 | 描述 |
|------|-----------|------|----------|-------------|
| `svg` | SVG | 是 | - | 要保存到磁盘的 SVG 数据 |
| `filename_prefix` | STRING | 是 | - | 保存文件的前缀。可包含格式化信息，例如 `%date:yyyy-MM-dd%` 或 `%Empty Latent Image.width%` 以包含来自节点的值。（默认值："svg/ComfyUI"） |

## 输出参数

| 输出名称 | 数据类型 | 描述 |
|----------|-----------|-------------|
| `ui` | DICT | 返回文件信息，包括文件名、子文件夹和类型，用于在 ComfyUI 界面中显示 |

**注意：** 此节点在可用时会自动将工作流元数据（提示信息和额外的 PNG 信息）嵌入 SVG 文件。元数据以 CDATA 段的形式插入到 SVG 的 metadata 元素中。
