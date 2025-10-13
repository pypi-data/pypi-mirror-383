> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/StringCompare/zh.md)

StringCompare 节点使用不同的比较方法来比较两个文本字符串。它可以检查一个字符串是否以另一个字符串开头、是否以另一个字符串结尾，或者两个字符串是否完全相等。比较时可以选择是否考虑字母大小写差异。

## 输入参数

| 参数 | 数据类型 | 必填 | 取值范围 | 描述 |
|-----------|-----------|----------|-------|-------------|
| `string_a` | STRING | 是 | - | 要比较的第一个字符串 |
| `string_b` | STRING | 是 | - | 用于比较的第二个字符串 |
| `mode` | COMBO | 是 | "Starts With"<br>"Ends With"<br>"Equal" | 使用的比较方法 |
| `case_sensitive` | BOOLEAN | 否 | - | 比较时是否考虑字母大小写（默认值：true） |

## 输出参数

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `output` | BOOLEAN | 如果满足比较条件则返回 true，否则返回 false |
