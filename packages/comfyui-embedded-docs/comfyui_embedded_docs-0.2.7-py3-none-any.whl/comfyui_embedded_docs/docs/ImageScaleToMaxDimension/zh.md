> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/ImageScaleToMaxDimension/zh.md)

ImageScaleToMaxDimension 节点可将图像调整至指定最大尺寸范围内，同时保持原始宽高比。该节点会计算图像是纵向还是横向取向，然后将较大尺寸缩放至目标大小，同时按比例调整较小尺寸。该节点支持多种放大方法，以满足不同的质量和性能需求。

## 输入参数

| 参数 | 数据类型 | 必需 | 取值范围 | 描述 |
|------|-----------|------|----------|-------------|
| `image` | IMAGE | 是 | - | 需要缩放的输入图像 |
| `upscale_method` | STRING | 是 | "area"<br>"lanczos"<br>"bilinear"<br>"nearest-exact"<br>"bicubic" | 用于图像缩放的插值方法 |
| `largest_size` | INT | 是 | 0 到 16384 | 缩放后图像的最大尺寸（默认值：512） |

## 输出结果

| 输出名称 | 数据类型 | 描述 |
|----------|-----------|-------------|
| `image` | IMAGE | 最大尺寸与指定大小匹配的缩放后图像 |
