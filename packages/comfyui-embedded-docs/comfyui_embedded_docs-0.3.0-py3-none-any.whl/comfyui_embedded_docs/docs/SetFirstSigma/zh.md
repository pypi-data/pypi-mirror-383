> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/SetFirstSigma/zh.md)

SetFirstSigma 节点通过将序列中的第一个 sigma 值替换为自定义值来修改 sigma 值序列。它接收现有的 sigma 序列和新的 sigma 值作为输入，然后返回一个新的 sigma 序列，其中仅第一个元素被更改，而其他所有 sigma 值保持不变。

## 输入参数

| 参数名 | 数据类型 | 必需 | 取值范围 | 描述 |
|-----------|-----------|----------|-------|-------------|
| `sigmas` | SIGMAS | 是 | - | 待修改的输入 sigma 值序列 |
| `sigma` | FLOAT | 是 | 0.0 至 20000.0 | 设置为序列中第一个元素的新 sigma 值（默认值：136.0） |

## 输出结果

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `sigmas` | SIGMAS | 经过修改的 sigma 序列，其中第一个元素已被自定义 sigma 值替换 |
