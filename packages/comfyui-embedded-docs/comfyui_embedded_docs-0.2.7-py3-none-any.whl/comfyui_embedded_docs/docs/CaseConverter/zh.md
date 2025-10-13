> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/CaseConverter/zh.md)

## 概述

Case Converter 节点可将文本字符串转换为不同的字母大小写格式。它接收输入字符串并根据所选模式进行转换，生成应用了指定大小写格式的输出字符串。该节点支持四种不同的大小写转换选项，用于修改文本的大小写格式。

## 输入

| 参数 | 数据类型 | 输入类型 | 默认值 | 范围 | 描述 |
|-----------|-----------|------------|---------|-------|-------------|
| `string` | STRING | 字符串 | - | - | 需要转换为不同大小写格式的文本字符串 |
| `mode` | STRING | 下拉选项 | - | ["UPPERCASE", "lowercase", "Capitalize", "Title Case"] | 要应用的大小写转换模式：UPPERCASE 将所有字母转换为大写，lowercase 将所有字母转换为小写，Capitalize 仅首字母大写，Title Case 将每个单词的首字母大写 |

## 输出

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `output` | STRING | 已转换为指定大小写格式的输入字符串 |
