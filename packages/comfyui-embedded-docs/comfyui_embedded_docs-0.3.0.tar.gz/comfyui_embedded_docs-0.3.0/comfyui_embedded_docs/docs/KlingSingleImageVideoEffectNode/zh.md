> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/KlingSingleImageVideoEffectNode/zh.md)

## 概述

Kling 单图视频特效节点基于单张参考图像创建具有不同特殊效果的视频。它应用各种视觉效果和场景，将静态图像转换为动态视频内容。该节点支持不同的特效场景、模型选项和视频时长，以实现所需的视觉效果。

## 输入

| 参数 | 数据类型 | 必填 | 范围 | 描述 |
|-----------|-----------|----------|-------|-------------|
| `image` | IMAGE | 是 | - | 参考图像。URL 或 Base64 编码字符串（不带 data:image 前缀）。文件大小不能超过 10MB，分辨率不低于 300*300px，宽高比在 1:2.5 ~ 2.5:1 之间 |
| `effect_scene` | COMBO | 是 | KlingSingleImageEffectsScene 中的选项 | 应用于视频生成的特效场景类型 |
| `model_name` | COMBO | 是 | KlingSingleImageEffectModelName 中的选项 | 用于生成视频特效的具体模型 |
| `duration` | COMBO | 是 | KlingVideoGenDuration 中的选项 | 生成视频的长度 |

**注意：** `effect_scene`、`model_name` 和 `duration` 的具体选项由其各自枚举类（KlingSingleImageEffectsScene、KlingSingleImageEffectModelName 和 KlingVideoGenDuration）中的可用值决定。

## 输出

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `video_id` | VIDEO | 应用了特效的生成视频 |
| `duration` | STRING | 生成视频的唯一标识符 |
| `duration` | STRING | 生成视频的时长 |
