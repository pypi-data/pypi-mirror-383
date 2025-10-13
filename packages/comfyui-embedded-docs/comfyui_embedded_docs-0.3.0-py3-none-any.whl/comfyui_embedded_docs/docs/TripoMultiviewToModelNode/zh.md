> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/TripoMultiviewToModelNode/zh.md)

此节点通过处理最多四张展示物体不同视角的图像，使用 Tripo 的 API 同步生成 3D 模型。它需要一张正面图像和至少一张额外视角（左侧、背面或右侧）图像，以创建具有纹理和材质选项的完整 3D 模型。

## 输入参数

| 参数 | 数据类型 | 必需 | 取值范围 | 描述 |
|-----------|-----------|----------|-------|-------------|
| `image` | IMAGE | 是 | - | 物体的正面视角图像（必需） |
| `image_left` | IMAGE | 否 | - | 物体的左侧视角图像 |
| `image_back` | IMAGE | 否 | - | 物体的背面视角图像 |
| `image_right` | IMAGE | 否 | - | 物体的右侧视角图像 |
| `model_version` | COMBO | 否 | 提供多个选项 | 用于生成的 Tripo 模型版本 |
| `orientation` | COMBO | 否 | 提供多个选项 | 3D 模型的方向设置 |
| `texture` | BOOLEAN | 否 | - | 是否为模型生成纹理（默认：True） |
| `pbr` | BOOLEAN | 否 | - | 是否生成 PBR（基于物理的渲染）材质（默认：True） |
| `model_seed` | INT | 否 | - | 模型生成的随机种子（默认：42） |
| `texture_seed` | INT | 否 | - | 纹理生成的随机种子（默认：42） |
| `texture_quality` | COMBO | 否 | "standard"<br>"detailed" | 纹理生成的质量级别（默认："standard"） |
| `texture_alignment` | COMBO | 否 | "original_image"<br>"geometry" | 将纹理对齐到模型的方法（默认："original_image"） |
| `face_limit` | INT | 否 | -1 到 500000 | 生成模型中的最大面数，-1 表示无限制（默认：-1） |
| `quad` | BOOLEAN | 否 | - | 是否生成基于四边形的几何体而非三角形（默认：False） |

**注意：** 正面图像（`image`）始终是必需的。必须提供至少一张额外的视角图像（`image_left`、`image_back` 或 `image_right`）以进行多视角处理。

## 输出结果

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `model_file` | STRING | 生成的 3D 模型的文件路径或标识符 |
| `model task_id` | MODEL_TASK_ID | 用于跟踪模型生成过程的任务标识符 |
