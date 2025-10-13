> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/StringSubstring/zh.md)

StringSubstring 节点用于从较长的文本字符串中提取部分内容。它通过起始位置和结束位置来定义需要提取的文本区间，并返回这两个位置之间的文本内容。

## 输入参数

| 参数名 | 数据类型 | 必填 | 取值范围 | 描述 |
|--------|----------|------|----------|------|
| `string` | STRING | 是 | - | 用于提取子串的输入文本字符串 |
| `start` | INT | 是 | - | 子串的起始位置索引 |
| `end` | INT | 是 | - | 子串的结束位置索引 |

## 输出结果

| 输出名称 | 数据类型 | 描述 |
|----------|----------|------|
| `output` | STRING | 从输入文本中提取出的子串 |
