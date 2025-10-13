> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/ByteDanceImageEditNode/zh.md)

字节跳动图像编辑节点允许您通过 API 使用字节跳动的 AI 模型来修改图像。您提供输入图像和描述所需更改的文本提示，节点会根据您的指令处理图像。该节点会自动处理 API 通信并返回编辑后的图像。

## 输入参数

| 参数名 | 数据类型 | 输入类型 | 默认值 | 取值范围 | 描述 |
|-----------|-----------|------------|---------|-------|-------------|
| `model` | MODEL | COMBO | seededit_3 | Image2ImageModelName 选项 | 模型名称 |
| `image` | IMAGE | IMAGE | - | - | 要编辑的基础图像 |
| `prompt` | STRING | STRING | "" | - | 编辑图像的指令 |
| `seed` | INT | INT | 0 | 0-2147483647 | 生成使用的随机种子 |
| `guidance_scale` | FLOAT | FLOAT | 5.5 | 1.0-10.0 | 数值越高，图像越紧密遵循提示 |
| `watermark` | BOOLEAN | BOOLEAN | True | - | 是否在图像上添加"AI 生成"水印 |

## 输出参数

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `IMAGE` | IMAGE | 从字节跳动 API 返回的编辑后图像 |
