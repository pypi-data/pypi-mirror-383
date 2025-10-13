> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/StringConcatenate/zh.md)

StringConcatenate 节点通过指定的分隔符将两个文本字符串合并为一个。它接收两个输入字符串和一个分隔字符或字符串，然后输出单个字符串，其中两个输入字符串通过分隔符连接在一起。

## 输入参数

| 参数 | 数据类型 | 必填 | 取值范围 | 描述 |
|-----------|-----------|----------|-------|-------------|
| `string_a` | STRING | 是 | - | 要连接的第一个文本字符串 |
| `string_b` | STRING | 是 | - | 要连接的第二个文本字符串 |
| `delimiter` | STRING | 否 | - | 在两个输入字符串之间插入的字符或字符串（默认为空字符串） |

## 输出结果

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `output` | STRING | 在 string_a 和 string_b 之间插入分隔符后的组合字符串 |
