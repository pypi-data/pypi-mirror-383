> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/Pikaffects/zh.md)

Pikaffects 节点可生成应用了各种视觉效果到输入图像的视频。它利用 Pika 的视频生成 API，将静态图像转换为具有特定效果（如融化、爆炸或悬浮）的动画视频。该节点需要 API 密钥和认证令牌才能访问 Pika 服务。

## 输入参数

| 参数 | 数据类型 | 必填 | 取值范围 | 描述 |
|-----------|-----------|----------|-------|-------------|
| `image` | IMAGE | 是 | - | 要应用 Pikaffect 效果的参考图像。 |
| `pikaffect` | COMBO | 是 | "Cake-ify"<br>"Crumble"<br>"Crush"<br>"Decapitate"<br>"Deflate"<br>"Dissolve"<br>"Explode"<br>"Eye-pop"<br>"Inflate"<br>"Levitate"<br>"Melt"<br>"Peel"<br>"Poke"<br>"Squish"<br>"Ta-da"<br>"Tear" | 要应用于图像的具体视觉效果（默认："Cake-ify"）。 |
| `prompt_text` | STRING | 是 | - | 指导视频生成的文本描述。 |
| `negative_prompt` | STRING | 是 | - | 描述生成视频中应避免内容的文本。 |
| `seed` | INT | 是 | 0 至 4294967295 | 用于可重现结果的随机种子值。 |

## 输出结果

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `output` | VIDEO | 应用了 Pikaffect 效果后生成的视频。 |
