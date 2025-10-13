> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/PrimitiveFloat/zh.md)

PrimitiveFloat 节点用于创建可在工作流中使用的浮点数值。它接收单个数字输入并输出相同的值，使您能够在 ComfyUI 流程中的不同节点之间定义和传递浮点数值。

## 输入参数

| 参数名 | 数据类型 | 必填 | 取值范围 | 描述 |
|-----------|-----------|----------|-------|-------------|
| `值` | FLOAT | 是 | -sys.maxsize 到 sys.maxsize | 要输出的浮点数值 |

## 输出结果

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `output` | FLOAT | 输入的浮点数值 |
