> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/KlingImageGenerationNode/zh.md)

Kling 图像生成节点能够根据文本提示生成图像，并可选使用参考图像进行引导。该节点基于您的文本描述和参考设置创建一张或多张图像，然后将生成的图像作为输出返回。

## 输入参数

| 参数 | 数据类型 | 必需 | 取值范围 | 描述 |
|-----------|-----------|----------|-------|-------------|
| `prompt` | STRING | 是 | - | 正向文本提示 |
| `negative_prompt` | STRING | 是 | - | 负向文本提示 |
| `image_type` | COMBO | 是 | KlingImageGenImageReferenceType 中的选项<br>（从源代码提取） | 图像参考类型选择 |
| `image_fidelity` | FLOAT | 是 | 0.0 - 1.0 | 用户上传图像的参考强度（默认值：0.5） |
| `human_fidelity` | FLOAT | 是 | 0.0 - 1.0 | 主体参考相似度（默认值：0.45） |
| `model_name` | COMBO | 是 | "kling-v1"<br>（及 KlingImageGenModelName 中的其他选项） | 图像生成的模型选择（默认值："kling-v1"） |
| `aspect_ratio` | COMBO | 是 | "16:9"<br>（及 KlingImageGenAspectRatio 中的其他选项） | 生成图像的宽高比（默认值："16:9"） |
| `n` | INT | 是 | 1 - 9 | 生成图像的数量（默认值：1） |
| `image` | IMAGE | 否 | - | 可选的参考图像 |

**参数约束：**

- `image` 参数是可选的，但当提供参考图像时，kling-v1 模型不支持参考图像功能
- 正向提示和负向提示有最大长度限制（MAX_PROMPT_LENGTH_IMAGE_GEN）
- 当未提供参考图像时，`image_type` 参数会自动设置为 None

## 输出参数

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `output` | IMAGE | 基于输入参数生成的图像 |
