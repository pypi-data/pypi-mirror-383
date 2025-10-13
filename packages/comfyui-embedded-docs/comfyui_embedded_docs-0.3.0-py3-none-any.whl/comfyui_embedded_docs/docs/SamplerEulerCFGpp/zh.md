> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/SamplerEulerCFGpp/zh.md)

SamplerEulerCFGpp 节点提供了一种用于生成输出的 Euler CFG++ 采样方法。该节点提供了两种不同实现版本的 Euler CFG++ 采样器，用户可根据偏好进行选择。

## 输入参数

| 参数 | 数据类型 | 必需 | 取值范围 | 描述 |
|-----------|-----------|----------|-------|-------------|
| `版本` | STRING | 是 | `"regular"`<br>`"alternative"` | 要使用的 Euler CFG++ 采样器的实现版本 |

## 输出结果

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `sampler` | SAMPLER | 返回一个配置好的 Euler CFG++ 采样器实例 |
