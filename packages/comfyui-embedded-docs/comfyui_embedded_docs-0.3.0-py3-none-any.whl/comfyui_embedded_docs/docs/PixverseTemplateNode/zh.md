> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/PixverseTemplateNode/zh.md)

PixVerse Template 节点允许您从可用的 PixVerse 视频生成模板中进行选择。它会将您选择的模板名称转换为 PixVerse API 创建视频所需的相应模板 ID。

## 输入参数

| 参数 | 数据类型 | 必需 | 取值范围 | 描述 |
|-----------|-----------|----------|-------|-------------|
| `模板` | STRING | 是 | 提供多个选项 | 用于 PixVerse 视频生成的模板。可用选项对应 PixVerse 系统中的预定义模板。 |

## 输出结果

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `pixverse_template` | INT | 与所选模板名称对应的模板 ID，可供其他 PixVerse 节点用于视频生成。 |
