> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/RecraftColorRGB/zh.md)

通过选择特定的 RGB 值创建 Recraft 颜色。此节点允许您通过指定独立的红、绿、蓝值来定义颜色，这些值随后会被转换为可在其他 Recraft 操作中使用的 Recraft 颜色格式。

## 输入参数

| 参数 | 数据类型 | 必填 | 取值范围 | 描述 |
|-----------|-----------|----------|-------|-------------|
| `r` | INT | 是 | 0-255 | 颜色的红色值（默认：0） |
| `g` | INT | 是 | 0-255 | 颜色的绿色值（默认：0） |
| `b` | INT | 是 | 0-255 | 颜色的蓝色值（默认：0） |
| `recraft_color` | COLOR | 否 | - | 用于扩展的可选现有 Recraft 颜色 |

## 输出结果

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `recraft_color` | COLOR | 创建的包含指定 RGB 值的 Recraft 颜色对象 |
