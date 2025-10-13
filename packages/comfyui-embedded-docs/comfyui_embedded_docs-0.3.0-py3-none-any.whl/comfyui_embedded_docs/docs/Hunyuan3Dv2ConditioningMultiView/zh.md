> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/Hunyuan3Dv2ConditioningMultiView/zh.md)

Hunyuan3Dv2ConditioningMultiView 节点处理多视角 CLIP 视觉嵌入以用于 3D 视频生成。它接收可选的前、左、后、右视角嵌入，并将它们与位置编码结合，为视频模型创建条件数据。该节点输出来自组合嵌入的正向条件数据，以及具有零值的负向条件数据。

## 输入参数

| 参数 | 数据类型 | 必需 | 取值范围 | 描述 |
|-----------|-----------|----------|-------|-------------|
| `前` | CLIP_VISION_OUTPUT | 否 | - | 前视角的 CLIP 视觉输出 |
| `左` | CLIP_VISION_OUTPUT | 否 | - | 左视角的 CLIP 视觉输出 |
| `后` | CLIP_VISION_OUTPUT | 否 | - | 后视角的 CLIP 视觉输出 |
| `右` | CLIP_VISION_OUTPUT | 否 | - | 右视角的 CLIP 视觉输出 |

**注意：** 节点需要至少提供一个视角输入才能正常工作。节点只会处理包含有效 CLIP 视觉输出数据的视角。

## 输出结果

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `反向` | CONDITIONING | 包含带位置编码的组合多视角嵌入的正向条件数据 |
| `negative` | CONDITIONING | 用于对比学习的零值负向条件数据 |
