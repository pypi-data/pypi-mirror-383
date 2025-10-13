> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/PhotoMakerLoader/zh.md)

PhotoMakerLoader 节点从可用的模型文件中加载 PhotoMaker 模型。它会读取指定的模型文件，并准备用于基于身份的图像生成任务的 PhotoMaker ID 编码器。此节点标记为实验性，仅供测试用途。

## 输入参数

| 参数名 | 数据类型 | 是否必需 | 取值范围 | 描述 |
|-----------|-----------|----------|-------|-------------|
| `photomaker模型名称` | STRING | 是 | 提供多个选项 | 要加载的 PhotoMaker 模型文件名。可用选项由 photomaker 文件夹中的模型文件决定。 |

## 输出结果

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `photomaker_model` | PHOTOMAKER | 已加载的 PhotoMaker 模型，包含 ID 编码器，可用于身份编码操作。 |
