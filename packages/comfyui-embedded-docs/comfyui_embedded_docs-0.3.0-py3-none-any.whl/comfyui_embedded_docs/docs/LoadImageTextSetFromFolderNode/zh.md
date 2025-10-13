> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/LoadImageTextSetFromFolderNode/zh.md)

从指定目录加载一批图像及其对应的文本描述，用于训练目的。该节点会自动搜索图像文件及其关联的文本描述文件，根据指定的调整尺寸设置处理图像，并使用提供的 CLIP 模型对描述文本进行编码。

## 输入参数

| 参数名 | 数据类型 | 必填 | 取值范围 | 描述 |
|-----------|-----------|----------|-------|-------------|
| `folder` | STRING | 是 | - | 要从中加载图像的文件夹路径。 |
| `clip` | CLIP | 是 | - | 用于编码文本的 CLIP 模型。 |
| `resize_method` | COMBO | 否 | "None"<br>"Stretch"<br>"Crop"<br>"Pad" | 用于调整图像尺寸的方法（默认："None"）。 |
| `width` | INT | 否 | -1 到 10000 | 调整图像后的宽度。-1 表示使用原始宽度（默认：-1）。 |
| `height` | INT | 否 | -1 到 10000 | 调整图像后的高度。-1 表示使用原始高度（默认：-1）。 |

**注意：** CLIP 输入必须有效且不能为 None。如果 CLIP 模型来自检查点加载器节点，请确保检查点包含有效的 CLIP 或文本编码器模型。

## 输出结果

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `IMAGE` | IMAGE | 加载并处理后的图像批次。 |
| `CONDITIONING` | CONDITIONING | 从文本描述编码得到的条件数据。 |
