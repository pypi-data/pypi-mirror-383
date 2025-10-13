> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/RegexMatch/zh.md)

RegexMatch 节点用于检查文本字符串是否与指定的正则表达式模式匹配。它会在输入字符串中搜索正则表达式模式的任何出现位置，并返回是否找到匹配项。您可以配置各种正则表达式标志，如大小写敏感性、多行模式和点号匹配模式，以控制模式匹配的行为方式。

## 输入参数

| 参数 | 数据类型 | 必填 | 取值范围 | 描述 |
|-----------|-----------|----------|-------|-------------|
| `string` | STRING | 是 | - | 需要搜索匹配项的文本字符串 |
| `regex_pattern` | STRING | 是 | - | 用于与字符串匹配的正则表达式模式 |
| `case_insensitive` | BOOLEAN | 否 | - | 匹配时是否忽略大小写（默认值：True） |
| `multiline` | BOOLEAN | 否 | - | 是否启用正则表达式匹配的多行模式（默认值：False） |
| `dotall` | BOOLEAN | 否 | - | 是否启用正则表达式匹配的点号匹配模式（默认值：False） |

## 输出参数

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `matches` | BOOLEAN | 如果正则表达式模式匹配输入字符串的任何部分则返回 True，否则返回 False |
