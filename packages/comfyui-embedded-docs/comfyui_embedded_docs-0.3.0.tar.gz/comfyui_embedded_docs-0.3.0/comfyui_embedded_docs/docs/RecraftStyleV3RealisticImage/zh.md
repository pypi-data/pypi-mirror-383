> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/RecraftStyleV3RealisticImage/zh.md)

## 概述

此节点创建用于 Recraft API 的现实主义图像风格配置。它允许您选择 realistic_image 风格，并从多种子风格选项中选择以自定义输出外观。

## 输入

| 参数 | 数据类型 | 必需 | 取值范围 | 描述 |
|-----------|-----------|----------|-------|-------------|
| `子风格` | STRING | 是 | 提供多个选项 | 应用于 realistic_image 风格的具体子风格。如果设置为 "None"，将不应用任何子风格。 |

## 输出

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `recraft_style` | STYLEV3 | 返回包含 realistic_image 风格和所选子风格设置的 Recraft 风格配置对象。 |
