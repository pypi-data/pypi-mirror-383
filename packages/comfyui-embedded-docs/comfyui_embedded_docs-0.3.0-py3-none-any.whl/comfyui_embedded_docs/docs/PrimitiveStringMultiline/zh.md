> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/PrimitiveStringMultiline/zh.md)

PrimitiveStringMultiline 节点提供了一个多行文本输入字段，用于在工作流中输入和传递字符串值。它接受包含多行的文本输入，并原样输出相同的字符串值。当需要输入较长文本内容或跨多行的格式化文本时，此节点非常有用。

## 输入参数

| 参数 | 数据类型 | 必填 | 取值范围 | 描述 |
|-----------|-----------|----------|-------|-------------|
| `值` | STRING | 是 | 无限制 | 可跨多行的文本输入值 |

## 输出结果

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `output` | STRING | 与输入值完全相同的字符串 |
