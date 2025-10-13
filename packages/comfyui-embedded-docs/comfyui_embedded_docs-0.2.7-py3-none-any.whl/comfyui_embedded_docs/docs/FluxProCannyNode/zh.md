> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/FluxProCannyNode/zh.md)

使用控制图像（canny）生成图像。该节点接收控制图像，根据提供的提示词生成新图像，同时遵循在控制图像中检测到的边缘结构。

## 输入参数

| 参数名 | 数据类型 | 必填 | 取值范围 | 描述 |
|-----------|-----------|----------|-------|-------------|
| `control_image` | IMAGE | 是 | - | 用于 canny 边缘检测控制的输入图像 |
| `prompt` | STRING | 否 | - | 图像生成的提示词（默认：空字符串） |
| `prompt_upsampling` | BOOLEAN | 否 | - | 是否对提示词进行上采样处理。如果启用，会自动修改提示词以实现更具创意的生成，但结果具有不确定性（相同的种子不会产生完全相同的结果）（默认：False） |
| `canny_low_threshold` | FLOAT | 否 | 0.01 - 0.99 | Canny 边缘检测的低阈值；如果 skip_processing 为 True 则忽略此参数（默认：0.1） |
| `canny_high_threshold` | FLOAT | 否 | 0.01 - 0.99 | Canny 边缘检测的高阈值；如果 skip_processing 为 True 则忽略此参数（默认：0.4） |
| `skip_preprocessing` | BOOLEAN | 否 | - | 是否跳过预处理；如果 control_image 已经是 canny 处理后的图像则设为 True，如果是原始图像则设为 False（默认：False） |
| `guidance` | FLOAT | 否 | 1 - 100 | 图像生成过程的引导强度（默认：30） |
| `steps` | INT | 否 | 15 - 50 | 图像生成过程的步数（默认：50） |
| `seed` | INT | 否 | 0 - 18446744073709551615 | 用于创建噪声的随机种子（默认：0） |

**注意：** 当 `skip_preprocessing` 设置为 True 时，`canny_low_threshold` 和 `canny_high_threshold` 参数将被忽略，因为此时假定控制图像已经是经过 canny 边缘处理的图像。

## 输出结果

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `output_image` | IMAGE | 基于控制图像和提示词生成的图像 |
