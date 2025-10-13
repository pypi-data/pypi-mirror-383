> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/ModelPatchLoader/zh.md)

> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！[在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/ModelPatchLoader/en.md)

ModelPatchLoader 节点从 model_patches 文件夹加载专门的模型补丁。它会自动检测补丁文件的类型并加载相应的模型架构，然后将其封装在 ModelPatcher 中以供工作流使用。此节点支持不同的补丁类型，包括 controlnet 块和特征嵌入器模型。

## 输入参数

| 参数 | 数据类型 | 必填 | 取值范围 | 描述 |
|------|-----------|------|----------|------|
| `name` | STRING | 是 | model_patches 文件夹中所有可用的模型补丁文件 | 要从 model_patches 目录加载的模型补丁文件名 |

## 输出结果

| 输出名称 | 数据类型 | 描述 |
|----------|-----------|------|
| `MODEL_PATCH` | MODEL_PATCH | 已加载的模型补丁，封装在 ModelPatcher 中供工作流使用 |
