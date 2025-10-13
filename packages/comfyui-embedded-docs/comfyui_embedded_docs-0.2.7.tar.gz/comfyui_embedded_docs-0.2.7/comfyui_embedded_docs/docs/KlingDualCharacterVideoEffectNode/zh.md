> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/KlingDualCharacterVideoEffectNode/zh.md)

Kling 双角色视频特效节点可根据所选场景创建带有特效的视频。该节点接收两张图像，并将第一张图像定位在合成视频的左侧，第二张图像定位在右侧。根据选择的不同特效场景，会应用不同的视觉效果。

## 输入参数

| 参数名称 | 数据类型 | 必填 | 取值范围 | 参数说明 |
|-----------|-----------|----------|-------|-------------|
| `image_left` | IMAGE | 是 | - | 左侧图像 |
| `image_right` | IMAGE | 是 | - | 右侧图像 |
| `effect_scene` | COMBO | 是 | 多个选项可选 | 应用于视频生成的特效场景类型 |
| `model_name` | COMBO | 否 | 多个选项可选 | 用于角色特效的模型（默认："kling-v1"） |
| `mode` | COMBO | 否 | 多个选项可选 | 视频生成模式（默认："std"） |
| `duration` | COMBO | 是 | 多个选项可选 | 生成视频的时长 |

## 输出结果

| 输出名称 | 数据类型 | 输出说明 |
|-------------|-----------|-------------|
| `duration` | VIDEO | 生成的双角色特效视频 |
| `duration` | STRING | 生成视频的时长信息 |
