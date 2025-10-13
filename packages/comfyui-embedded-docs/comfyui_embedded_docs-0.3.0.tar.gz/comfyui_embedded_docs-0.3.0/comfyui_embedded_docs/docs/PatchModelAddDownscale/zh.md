> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/PatchModelAddDownscale/zh.md)

PatchModelAddDownscale 节点通过向模型中的特定块应用下采样和上采样操作，实现了 Kohya Deep Shrink 功能。它在处理过程中降低中间特征的分辨率，然后将其恢复到原始尺寸，这可以在保持质量的同时提升性能。该节点允许精确控制在模型执行过程中这些缩放操作的发生时机和方式。

## 输入参数

| 参数名 | 数据类型 | 必需 | 取值范围 | 描述 |
|-----------|-----------|----------|-------|-------------|
| `模型` | MODEL | 是 | - | 要应用下采样补丁的模型 |
| `层编号` | INT | 否 | 1-32 | 将应用下采样的具体块编号（默认值：3） |
| `收缩系数` | FLOAT | 否 | 0.1-9.0 | 特征下采样的比例因子（默认值：2.0） |
| `开始百分比` | FLOAT | 否 | 0.0-1.0 | 去噪过程中开始下采样的起始点（默认值：0.0） |
| `结束百分比` | FLOAT | 否 | 0.0-1.0 | 去噪过程中停止下采样的结束点（默认值：0.35） |
| `跳过后收缩` | BOOLEAN | 否 | - | 是否在跳跃连接后应用下采样（默认值：True） |
| `收缩算法` | COMBO | 否 | "bicubic"<br>"nearest-exact"<br>"bilinear"<br>"area"<br>"bislerp" | 用于下采样操作的插值方法 |
| `放大方法` | COMBO | 否 | "bicubic"<br>"nearest-exact"<br>"bilinear"<br>"area"<br>"bislerp" | 用于上采样操作的插值方法 |

## 输出结果

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `模型` | MODEL | 应用了下采样补丁的修改后模型 |
