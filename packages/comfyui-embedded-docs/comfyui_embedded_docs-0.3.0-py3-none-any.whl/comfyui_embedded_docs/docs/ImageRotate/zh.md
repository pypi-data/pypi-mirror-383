> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/ImageRotate/zh.md)

ImageRotate 节点可将输入图像按指定角度进行旋转。它支持四种旋转选项：不旋转、顺时针90度、180度以及顺时针270度。该节点采用高效的张量运算来执行旋转操作，能够完整保持图像数据完整性。

## 输入参数

| 参数 | 数据类型 | 必填 | 取值范围 | 描述 |
|-----------|-----------|----------|-------|-------------|
| `image` | IMAGE | 是 | - | 需要旋转的输入图像 |
| `rotation` | STRING | 是 | "none"<br>"90 degrees"<br>"180 degrees"<br>"270 degrees" | 要应用于图像的旋转角度 |

## 输出结果

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `image` | IMAGE | 旋转后的输出图像 |
