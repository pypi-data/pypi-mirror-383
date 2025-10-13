> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/LumaConceptsNode/zh.md)

## 概述

持有一个或多个相机概念，用于 Luma 文生视频和 Luma 图生视频节点。此节点允许您选择最多四个相机概念，并可选择将它们与现有概念链组合使用。

## 输入

| 参数 | 数据类型 | 必需 | 取值范围 | 描述 |
|-----------|-----------|----------|-------|-------------|
| `concept1` | STRING | 是 | 提供多个选项<br>包含"None"选项 | 从可用的 Luma 概念中选择第一个相机概念 |
| `concept2` | STRING | 是 | 提供多个选项<br>包含"None"选项 | 从可用的 Luma 概念中选择第二个相机概念 |
| `concept3` | STRING | 是 | 提供多个选项<br>包含"None"选项 | 从可用的 Luma 概念中选择第三个相机概念 |
| `concept4` | STRING | 是 | 提供多个选项<br>包含"None"选项 | 从可用的 Luma 概念中选择第四个相机概念 |
| `luma_concepts` | LUMA_CONCEPTS | 否 | 不适用 | 可选的相机概念，用于添加到此处选择的概念中 |

**注意：** 如果您不想使用全部四个概念插槽，所有概念参数（`concept1` 到 `concept4`）都可以设置为"None"。该节点会将任何提供的 `luma_concepts` 与选定的概念合并，以创建组合的概念链。

## 输出

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `luma_concepts` | LUMA_CONCEPTS | 包含所有选定概念的组合相机概念链 |
