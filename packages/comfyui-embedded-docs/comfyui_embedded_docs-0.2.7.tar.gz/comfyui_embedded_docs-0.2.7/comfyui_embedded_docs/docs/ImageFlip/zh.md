> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/ImageFlip/zh.md)

ImageFlip 节点可沿不同轴向翻转图像。它能够沿 x 轴垂直翻转或沿 y 轴水平翻转图像。该节点基于选定方法使用 torch.flip 操作执行翻转。

## 输入参数

| 参数名称 | 数据类型 | 必填 | 取值范围 | 功能说明 |
|-----------|-----------|----------|-------|-------------|
| `image` | IMAGE | 是 | - | 待翻转的输入图像 |
| `flip_method` | STRING | 是 | "x-axis: vertically"<br>"y-axis: horizontally" | 需要应用的翻转方向 |

## 输出参数

| 输出名称 | 数据类型 | 功能说明 |
|-------------|-----------|-------------|
| `image` | IMAGE | 翻转后的输出图像 |
