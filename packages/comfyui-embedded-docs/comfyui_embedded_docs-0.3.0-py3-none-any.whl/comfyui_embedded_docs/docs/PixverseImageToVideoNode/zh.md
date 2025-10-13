> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/PixverseImageToVideoNode/zh.md)

## 概述

基于输入图像和文本提示生成视频。此节点接收一张图像，并通过应用指定的运动和质量设置，将静态图像转换为动态序列来创建动画视频。

## 输入

| 参数 | 数据类型 | 必需 | 范围 | 描述 |
|-----------|-----------|----------|-------|-------------|
| `图像` | IMAGE | 是 | - | 要转换为视频的输入图像 |
| `提示词` | STRING | 是 | - | 视频生成的提示词 |
| `质量` | COMBO | 是 | `res_540p`<br>`res_1080p` | 视频质量设置（默认：res_540p） |
| `时长（秒）` | COMBO | 是 | `dur_2`<br>`dur_5`<br>`dur_10` | 生成视频的持续时间（秒） |
| `运动模式` | COMBO | 是 | `normal`<br>`fast`<br>`slow`<br>`zoom_in`<br>`zoom_out`<br>`pan_left`<br>`pan_right`<br>`pan_up`<br>`pan_down`<br>`tilt_up`<br>`tilt_down`<br>`roll_clockwise`<br>`roll_counterclockwise` | 应用于视频生成的运动风格 |
| `种子` | INT | 是 | 0-2147483647 | 视频生成的随机种子（默认：0） |
| `反向提示词` | STRING | 否 | - | 图像中不希望出现的元素的可选文本描述 |
| `PixVerse 模板` | CUSTOM | 否 | - | 影响生成风格的可选模板，由 PixVerse 模板节点创建 |

**注意：** 使用 1080p 质量时，运动模式会自动设置为 normal，且持续时间限制为 5 秒。对于非 5 秒的持续时间，运动模式也会自动设置为 normal。

## 输出

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `output` | VIDEO | 基于输入图像和参数生成的视频 |
