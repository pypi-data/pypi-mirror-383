> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/CLIPMergeSubtract/zh.md)

> 本文档由 AI 生成，如果您发现任何错误或有改进建议，欢迎贡献！[在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/CLIPMergeSubtract/en.md)

CLIPMergeSubtract 节点通过从一个 CLIP 模型中减去另一个 CLIP 模型的权重来执行模型合并。它通过克隆第一个模型，然后减去第二个模型的关键补丁（附带可调节的乘数来控制减法强度）来创建新的 CLIP 模型。这允许通过从基础模型中移除特定特征来实现精细调整的模型混合。

## 输入参数

| 参数 | 数据类型 | 必填 | 取值范围 | 描述 |
|-----------|-----------|----------|-------|-------------|
| `clip1` | CLIP | 是 | - | 将被克隆和修改的基础 CLIP 模型 |
| `clip2` | CLIP | 是 | - | 其关键补丁将从基础模型中减去的 CLIP 模型 |
| `乘数` | FLOAT | 是 | -10.0 到 10.0 | 控制减法操作强度的乘数（默认值：1.0） |

**注意：** 无论乘数值如何，该节点都会从减法操作中排除 `.position_ids` 和 `.logit_scale` 参数。

## 输出结果

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `clip` | CLIP | 从第一个模型减去第二个模型权重后得到的 CLIP 模型 |
