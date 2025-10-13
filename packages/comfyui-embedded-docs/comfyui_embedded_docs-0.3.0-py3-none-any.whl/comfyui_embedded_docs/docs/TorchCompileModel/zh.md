> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/TorchCompileModel/zh.md)

TorchCompileModel 节点对模型应用 PyTorch 编译以优化其性能。它会创建输入模型的副本，并使用指定的后端通过 PyTorch 的编译功能对其进行封装。这可以提高模型在推理过程中的执行速度。

## 输入参数

| 参数 | 数据类型 | 必需 | 取值范围 | 描述 |
|-----------|-----------|----------|-------|-------------|
| `模型` | MODEL | 是 | - | 待编译和优化的模型 |
| `后端` | STRING | 是 | "inductor"<br>"cudagraphs" | 用于优化的 PyTorch 编译后端 |

## 输出结果

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `模型` | MODEL | 应用了 PyTorch 编译的已编译模型 |
