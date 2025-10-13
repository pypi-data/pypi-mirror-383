> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/PixverseTextToVideoNode/zh.md)

基于提示词和输出尺寸生成视频。此节点使用文本描述和各种生成参数通过 PixVerse API 创建视频内容，生成视频输出。

## 输入参数

| 参数 | 数据类型 | 必需 | 取值范围 | 描述 |
|-----------|-----------|----------|-------|-------------|
| `提示词` | STRING | 是 | - | 视频生成的提示词（默认：""） |
| `宽高比` | COMBO | 是 | PixverseAspectRatio 的选项 | 生成视频的宽高比 |
| `质量` | COMBO | 是 | PixverseQuality 的选项 | 视频质量设置（默认：PixverseQuality.res_540p） |
| `时长（秒）` | COMBO | 是 | PixverseDuration 的选项 | 生成视频的时长（单位：秒） |
| `运动模式` | COMBO | 是 | PixverseMotionMode 的选项 | 视频生成的运动风格 |
| `种子` | INT | 是 | 0 到 2147483647 | 视频生成的随机种子（默认：0） |
| `反向提示词` | STRING | 否 | - | 图像中不希望出现的元素的可选文本描述（默认：""） |
| `PixVerse 模板` | CUSTOM | 否 | - | 影响生成风格的可选模板，由 PixVerse 模板节点创建 |

**注意：** 当使用 1080p 质量时，运动模式会自动设置为 normal 且时长限制为 5 秒。对于非 5 秒的时长，运动模式也会自动设置为 normal。

## 输出结果

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `output` | VIDEO | 生成的视频文件 |
