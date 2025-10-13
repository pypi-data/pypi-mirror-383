> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/RegexExtract/zh.md)

RegexExtract 节点使用正则表达式在文本中搜索模式。它可以查找第一个匹配项、所有匹配项、匹配项中的特定组，或多个匹配项中的所有组。该节点支持多种正则表达式标志，用于控制大小写敏感性、多行匹配和 dotall 行为。

## 输入参数

| 参数 | 数据类型 | 必填 | 取值范围 | 描述 |
|-----------|-----------|----------|-------|-------------|
| `string` | STRING | 是 | - | 要搜索模式的输入文本 |
| `regex_pattern` | STRING | 是 | - | 要搜索的正则表达式模式 |
| `mode` | COMBO | 是 | "First Match"<br>"All Matches"<br>"First Group"<br>"All Groups" | 提取模式决定返回匹配项的哪些部分 |
| `case_insensitive` | BOOLEAN | 否 | - | 匹配时是否忽略大小写（默认：True） |
| `multiline` | BOOLEAN | 否 | - | 是否将字符串视为多行（默认：False） |
| `dotall` | BOOLEAN | 否 | - | 点号(.)是否匹配换行符（默认：False） |
| `group_index` | INT | 否 | 0-100 | 使用组模式时要提取的捕获组索引（默认：1） |

**注意：** 当使用"First Group"或"All Groups"模式时，`group_index` 参数指定要提取的捕获组。组0代表整个匹配项，而组1+代表正则表达式模式中编号的捕获组。

## 输出结果

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `output` | STRING | 根据所选模式和参数提取的文本 |
