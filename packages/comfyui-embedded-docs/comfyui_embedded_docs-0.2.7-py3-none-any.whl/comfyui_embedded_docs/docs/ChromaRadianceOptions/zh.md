> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/ChromaRadianceOptions/zh.md)

ChromaRadianceOptions 节点允许您配置 Chroma Radiance 模型的高级设置。它封装现有模型，并在去噪过程中根据 sigma 值应用特定选项，从而实现对 NeRF 图块大小和其他辐射相关参数的精细控制。

## 输入参数

| 参数 | 数据类型 | 输入类型 | 默认值 | 范围 | 描述 |
|-----------|-----------|------------|---------|-------|-------------|
| `model` | MODEL | 必填 | - | - | 要应用 Chroma Radiance 选项的模型 |
| `preserve_wrapper` | BOOLEAN | 可选 | True | - | 启用时，如果存在现有模型函数包装器，将委托给该包装器。通常应保持启用状态。 |
| `start_sigma` | FLOAT | 可选 | 1.0 | 0.0 - 1.0 | 这些选项开始生效的第一个 sigma 值。 |
| `end_sigma` | FLOAT | 可选 | 0.0 | 0.0 - 1.0 | 这些选项停止生效的最后一个 sigma 值。 |
| `nerf_tile_size` | INT | 可选 | -1 | -1 及以上 | 允许覆盖默认的 NeRF 图块大小。-1 表示使用默认值（32）。0 表示使用非分块模式（可能需要大量显存）。 |

**注意：** 仅当当前 sigma 值介于 `end_sigma` 和 `start_sigma` 之间（含边界值）时，Chroma Radiance 选项才会生效。`nerf_tile_size` 参数仅在设置为 0 或更高值时才会被应用。

## 输出参数

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `model` | MODEL | 应用了 Chroma Radiance 选项的修改后模型 |
