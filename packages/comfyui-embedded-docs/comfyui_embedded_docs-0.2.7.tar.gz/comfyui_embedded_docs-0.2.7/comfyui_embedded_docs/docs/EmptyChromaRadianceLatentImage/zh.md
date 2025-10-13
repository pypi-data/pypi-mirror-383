> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/EmptyChromaRadianceLatentImage/zh.md)

EmptyChromaRadianceLatentImage 节点创建一个具有指定尺寸的空白潜空间图像，用于色度辐射工作流程。它生成一个填充零值的张量，作为潜空间操作的起点。该节点允许您定义空白潜空间图像的宽度、高度和批次大小。

## 输入参数

| 参数 | 数据类型 | 必填 | 取值范围 | 描述 |
|-----------|-----------|----------|-------|-------------|
| `width` | INT | 是 | 16 到 MAX_RESOLUTION | 潜空间图像的宽度（单位：像素，默认值：1024，必须能被16整除） |
| `height` | INT | 是 | 16 到 MAX_RESOLUTION | 潜空间图像的高度（单位：像素，默认值：1024，必须能被16整除） |
| `batch_size` | INT | 否 | 1 到 4096 | 批次中生成的潜空间图像数量（默认值：1） |

## 输出结果

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `samples` | LATENT | 生成的具有指定尺寸的空白潜空间图像张量 |
