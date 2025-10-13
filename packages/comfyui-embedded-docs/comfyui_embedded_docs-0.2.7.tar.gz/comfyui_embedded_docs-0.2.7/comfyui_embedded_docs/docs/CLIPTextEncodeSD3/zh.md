> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/CLIPTextEncodeSD3/zh.md)

CLIPTextEncodeSD3 节点通过使用不同的 CLIP 模型对多个文本提示进行编码，为 Stable Diffusion 3 模型处理文本输入。它处理三个独立的文本输入（clip_g、clip_l 和 t5xxl），并提供管理空文本填充的选项。该节点确保不同文本输入之间的正确令牌对齐，并返回适用于 SD3 生成流程的条件数据。

## 输入参数

| 参数名称 | 数据类型 | 输入类型 | 默认值 | 取值范围 | 参数说明 |
|-----------|-----------|------------|---------|-------|-------------|
| `clip` | CLIP | 必需 | - | - | 用于文本编码的 CLIP 模型 |
| `clip_l` | STRING | 多行文本，动态提示 | - | - | 本地 CLIP 模型的文本输入 |
| `clip_g` | STRING | 多行文本，动态提示 | - | - | 全局 CLIP 模型的文本输入 |
| `t5xxl` | STRING | 多行文本，动态提示 | - | - | T5-XXL 模型的文本输入 |
| `空白填充` | COMBO | 选择 | - | ["none", "empty_prompt"] | 控制如何处理空文本输入 |

**参数约束：**

- 当 `empty_padding` 设置为 "none" 时，`clip_g`、`clip_l` 或 `t5xxl` 的空文本输入将产生空令牌列表而不是填充
- 当长度不同时，节点通过用空令牌填充较短的那个，自动平衡 `clip_l` 和 `clip_g` 输入之间的令牌长度
- 所有文本输入都支持动态提示和多行文本输入

## 输出结果

| 输出名称 | 数据类型 | 输出说明 |
|-------------|-----------|-------------|
| `CONDITIONING` | CONDITIONING | 已编码的文本条件数据，准备用于 SD3 生成流程 |
