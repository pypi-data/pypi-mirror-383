> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/RecraftStyleV3InfiniteStyleLibrary/zh.md)

此节点允许您使用预先存在的 UUID 从 Recraft 的无限风格库中选择样式。它会根据提供的样式标识符检索样式信息，并返回以供其他 Recraft 节点使用。

## 输入参数

| 参数 | 数据类型 | 必需 | 取值范围 | 描述 |
|-----------|-----------|----------|-------|-------------|
| `style_id` | STRING | 是 | 任何有效的 UUID | 无限风格库中的样式 UUID。 |

**注意：** `style_id` 输入不能为空。如果提供空字符串，节点将引发异常。

## 输出结果

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `recraft_style` | STYLEV3 | 从 Recraft 无限风格库中选择的样式对象 |
