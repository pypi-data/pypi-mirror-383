> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/USOStyleReference/zh.md)

USOStyleReference 节点使用来自 CLIP 视觉输出的编码图像特征，将风格参考补丁应用于模型。它通过从视觉输入中提取的风格信息创建输入模型的修改版本，从而实现风格迁移或基于参考的生成功能。

## 输入参数

| 参数 | 数据类型 | 必填 | 取值范围 | 描述 |
|-----------|-----------|----------|-------|-------------|
| `model` | MODEL | 是 | - | 要应用风格参考补丁的基础模型 |
| `model_patch` | MODEL_PATCH | 是 | - | 包含风格参考信息的模型补丁 |
| `clip_vision_output` | CLIP_VISION_OUTPUT | 是 | - | 从 CLIP 视觉处理中提取的编码视觉特征 |

## 输出结果

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `model` | MODEL | 应用了风格参考补丁的修改后模型 |
