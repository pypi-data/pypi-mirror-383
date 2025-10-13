> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/TripoConversionNode/zh.md)

TripoConversionNode 使用 Tripo API 在不同文件格式之间转换 3D 模型。它接收先前 Tripo 操作的任务 ID，并将结果模型转换为所需的格式，提供多种导出选项。

## 输入参数

| 参数名 | 数据类型 | 必填 | 取值范围 | 描述 |
|-----------|-----------|----------|-------|-------------|
| `original_model_task_id` | MODEL_TASK_ID,RIG_TASK_ID,RETARGET_TASK_ID | 是 | MODEL_TASK_ID<br>RIG_TASK_ID<br>RETARGET_TASK_ID | 来自先前 Tripo 操作（模型生成、骨骼绑定或重定向）的任务 ID |
| `format` | COMBO | 是 | GLTF<br>USDZ<br>FBX<br>OBJ<br>STL<br>3MF | 转换后 3D 模型的目标文件格式 |
| `quad` | BOOLEAN | 否 | True/False | 是否将三角形转换为四边形（默认值：False） |
| `face_limit` | INT | 否 | -1 到 500000 | 输出模型中的最大面数，使用 -1 表示无限制（默认值：-1） |
| `texture_size` | INT | 否 | 128 到 4096 | 输出纹理的像素尺寸（默认值：4096） |
| `texture_format` | COMBO | 否 | BMP<br>DPX<br>HDR<br>JPEG<br>OPEN_EXR<br>PNG<br>TARGA<br>TIFF<br>WEBP | 导出纹理的格式（默认值：JPEG） |

**注意：** `original_model_task_id` 必须是来自先前 Tripo 操作（模型生成、骨骼绑定或重定向）的有效任务 ID。

## 输出参数

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| *无命名输出* | - | 此节点异步处理转换，并通过 Tripo API 系统返回结果 |
