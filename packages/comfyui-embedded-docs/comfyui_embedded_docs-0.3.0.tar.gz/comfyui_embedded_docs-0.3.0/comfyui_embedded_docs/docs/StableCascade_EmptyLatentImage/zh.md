> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/StableCascade_EmptyLatentImage/zh.md)

StableCascade_EmptyLatentImage 节点为 Stable Cascade 模型创建空潜在张量。它生成两个独立的潜在表示——一个用于阶段 C，另一个用于阶段 B——根据输入分辨率和压缩设置具有适当的维度。该节点为 Stable Cascade 生成流程提供了起点。

## 输入参数

| 参数 | 数据类型 | 必填 | 取值范围 | 描述 |
|-----------|-----------|----------|-------|-------------|
| `宽度` | INT | 是 | 256 至 MAX_RESOLUTION | 输出图像的宽度（单位：像素）（默认值：1024，步长：8） |
| `高度` | INT | 是 | 256 至 MAX_RESOLUTION | 输出图像的高度（单位：像素）（默认值：1024，步长：8） |
| `压缩` | INT | 是 | 4 至 128 | 决定阶段 C 潜在维度的压缩因子（默认值：42，步长：1） |
| `批量大小` | INT | 否 | 1 至 4096 | 单批次生成的潜在样本数量（默认值：1） |

## 输出结果

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `阶段B` | LATENT | 阶段 C 潜在张量，维度为 [batch_size, 16, height//compression, width//compression] |
| `stage_b` | LATENT | 阶段 B 潜在张量，维度为 [batch_size, 4, height//4, width//4] |
