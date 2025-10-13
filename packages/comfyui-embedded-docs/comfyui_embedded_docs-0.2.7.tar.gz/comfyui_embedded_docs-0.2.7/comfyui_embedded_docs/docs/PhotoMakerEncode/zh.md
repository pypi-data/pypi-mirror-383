> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/PhotoMakerEncode/zh.md)

# PhotoMakerEncode 节点

PhotoMakerEncode 节点处理图像和文本，为 AI 图像生成生成条件数据。它接收参考图像和文本提示，然后创建可用于基于参考图像的视觉特征来引导图像生成的嵌入向量。该节点专门在文本中查找 "photomaker" 标记，以确定在何处应用基于图像的条件控制。

## 输入参数

| 参数 | 数据类型 | 必需 | 取值范围 | 描述 |
|-----------|-----------|----------|-------|-------------|
| `photomaker` | PHOTOMAKER | 是 | - | 用于处理图像和生成嵌入向量的 PhotoMaker 模型 |
| `图像` | IMAGE | 是 | - | 提供条件控制视觉特征的参考图像 |
| `clip` | CLIP | 是 | - | 用于文本标记化和编码的 CLIP 模型 |
| `文本` | STRING | 是 | - | 用于生成条件控制的文本提示（默认："photograph of photomaker"） |

**注意：** 当文本包含 "photomaker" 一词时，节点会在提示词中的该位置应用基于图像的条件控制。如果文本中未找到 "photomaker"，节点将生成没有图像影响的标准文本条件控制。

## 输出结果

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `CONDITIONING` | CONDITIONING | 包含图像和文本嵌入向量的条件数据，用于引导图像生成 |
