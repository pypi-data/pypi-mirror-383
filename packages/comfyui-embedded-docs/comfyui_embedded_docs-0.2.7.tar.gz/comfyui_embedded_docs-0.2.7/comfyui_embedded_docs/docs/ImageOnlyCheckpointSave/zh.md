> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/ImageOnlyCheckpointSave/zh.md)

ImageOnlyCheckpointSave 节点用于保存包含模型、CLIP 视觉编码器和 VAE 的检查点文件。它会创建具有指定文件名前缀的 safetensors 文件，并将其存储在输出目录中。该节点专门设计用于将图像相关的模型组件一起保存在单个检查点文件中。

## 输入参数

| 参数名 | 数据类型 | 必填 | 取值范围 | 描述 |
|--------|-----------|------|----------|------|
| `模型` | MODEL | 是 | - | 要保存到检查点中的模型 |
| `clip视觉` | CLIP_VISION | 是 | - | 要保存到检查点中的 CLIP 视觉编码器 |
| `vae` | VAE | 是 | - | 要保存到检查点中的 VAE（变分自编码器） |
| `文件名前缀` | STRING | 是 | - | 输出文件名的前缀（默认："checkpoints/ComfyUI"） |
| `prompt` | PROMPT | 否 | - | 用于工作流提示数据的隐藏参数 |
| `extra_pnginfo` | EXTRA_PNGINFO | 否 | - | 用于额外 PNG 元数据的隐藏参数 |

## 输出结果

| 输出名称 | 数据类型 | 描述 |
|----------|-----------|------|
| - | - | 此节点不返回任何输出 |
