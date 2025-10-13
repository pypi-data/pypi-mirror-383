> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/ResizeAndPadImage/zh.md)

ResizeAndPadImage 节点可将图像调整至指定尺寸范围内，同时保持原始宽高比例。该节点会按比例缩放图像以适应目标宽度和高度，随后在边缘区域添加填充以补足剩余空间。用户可自定义填充颜色和插值方法，从而控制填充区域的外观表现和图像缩放质量。

## 输入参数

| 参数名 | 数据类型 | 必填 | 取值范围 | 描述 |
|-----------|-----------|----------|-------|-------------|
| `image` | IMAGE | 是 | - | 需要调整尺寸并添加填充的输入图像 |
| `target_width` | INT | 是 | 1 至 MAX_RESOLUTION | 输出图像的目标宽度（默认值：512） |
| `target_height` | INT | 是 | 1 至 MAX_RESOLUTION | 输出图像的目标高度（默认值：512） |
| `padding_color` | COMBO | 是 | "white"<br>"black" | 用于调整后图像周边填充区域的颜色 |
| `interpolation` | COMBO | 是 | "area"<br>"bicubic"<br>"nearest-exact"<br>"bilinear"<br>"lanczos" | 用于图像尺寸调整的插值方法 |

## 输出结果

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `image` | IMAGE | 经过尺寸调整和填充处理后的输出图像 |
