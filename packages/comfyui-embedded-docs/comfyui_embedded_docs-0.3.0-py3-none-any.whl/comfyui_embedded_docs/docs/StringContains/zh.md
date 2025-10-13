> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/StringContains/zh.md)

StringContains 节点用于检查给定字符串是否包含指定的子字符串。该节点支持区分大小写或不区分大小写的匹配方式，并返回布尔值结果来指示是否在主字符串中找到了子字符串。

## 输入参数

| 参数 | 数据类型 | 必填 | 取值范围 | 描述 |
|-----------|-----------|----------|-------|-------------|
| `string` | STRING | 是 | - | 要搜索的主文本字符串 |
| `substring` | STRING | 是 | - | 在主字符串中要搜索的文本内容 |
| `case_sensitive` | BOOLEAN | 否 | - | 决定搜索是否区分大小写（默认值：true） |

## 输出结果

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `contains` | BOOLEAN | 如果在字符串中找到子字符串则返回 true，否则返回 false |
