> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/OpenAIDalle3/zh.md)

通过 OpenAI 的 DALL·E 3 端点同步生成图像。此节点接收文本提示词，并使用 OpenAI 的 DALL·E 3 模型创建相应图像，允许您指定图像质量、风格和尺寸。

## 输入参数

| 参数 | 数据类型 | 必填 | 取值范围 | 描述 |
|------|-----------|------|----------|------|
| `提示词` | STRING | 是 | - | 用于 DALL·E 的文本提示词（默认：""） |
| `种子` | INT | 否 | 0 到 2147483647 | 后端尚未实现（默认：0） |
| `质量` | COMBO | 否 | "standard"<br>"hd" | 图像质量（默认："standard"） |
| `风格` | COMBO | 否 | "natural"<br>"vivid" | Vivid 会使模型倾向于生成超真实和戏剧化的图像。Natural 会使模型生成更自然、不那么超真实的图像。（默认："natural"） |
| `尺寸` | COMBO | 否 | "1024x1024"<br>"1024x1792"<br>"1792x1024" | 图像尺寸（默认："1024x1024"） |

## 输出结果

| 输出名称 | 数据类型 | 描述 |
|----------|-----------|------|
| `IMAGE` | IMAGE | 由 DALL·E 3 生成的图像 |
