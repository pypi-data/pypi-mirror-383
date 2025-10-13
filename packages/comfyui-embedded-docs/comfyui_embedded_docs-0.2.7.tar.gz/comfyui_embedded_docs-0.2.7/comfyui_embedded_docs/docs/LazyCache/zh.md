> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/LazyCache/zh.md)

LazyCache 是 EasyCache 的自制版本，提供了更简易的实现方式。它兼容 ComfyUI 中的任何模型，并通过添加缓存功能来减少采样过程中的计算量。虽然其性能通常不如 EasyCache，但在某些罕见情况下可能更有效，且具有通用兼容性。

## 输入参数

| 参数名 | 数据类型 | 必填 | 取值范围 | 描述 |
|-----------|-----------|----------|-------|-------------|
| `model` | MODEL | 是 | - | 要添加 LazyCache 功能的模型 |
| `reuse_threshold` | FLOAT | 否 | 0.0 - 3.0 | 重用缓存步骤的阈值（默认值：0.2） |
| `start_percent` | FLOAT | 否 | 0.0 - 1.0 | 开始使用 LazyCache 的相对采样步数（默认值：0.15） |
| `end_percent` | FLOAT | 否 | 0.0 - 1.0 | 停止使用 LazyCache 的相对采样步数（默认值：0.95） |
| `verbose` | BOOLEAN | 否 | - | 是否输出详细日志信息（默认值：False） |

## 输出结果

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `model` | MODEL | 已添加 LazyCache 功能的模型 |
