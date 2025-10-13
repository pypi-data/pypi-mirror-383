> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/EasyCache/zh.md)

EasyCache 节点为模型实现了原生缓存系统，通过在采样过程中复用先前计算过的步骤来提升性能。该节点可为模型添加 EasyCache 功能，并支持配置在采样时间线中开始和停止使用缓存的阈值。

## 输入参数

| 参数名 | 数据类型 | 必填 | 取值范围 | 描述 |
|-----------|-----------|----------|-------|-------------|
| `model` | MODEL | 是 | - | 要添加 EasyCache 功能的模型。 |
| `reuse_threshold` | FLOAT | 否 | 0.0 - 3.0 | 复用缓存步骤的阈值（默认值：0.2）。 |
| `start_percent` | FLOAT | 否 | 0.0 - 1.0 | 开始使用 EasyCache 的相对采样步数（默认值：0.15）。 |
| `end_percent` | FLOAT | 否 | 0.0 - 1.0 | 停止使用 EasyCache 的相对采样步数（默认值：0.95）。 |
| `verbose` | BOOLEAN | 否 | - | 是否输出详细日志信息（默认值：False）。 |

## 输出结果

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `model` | MODEL | 已添加 EasyCache 功能的模型。 |
