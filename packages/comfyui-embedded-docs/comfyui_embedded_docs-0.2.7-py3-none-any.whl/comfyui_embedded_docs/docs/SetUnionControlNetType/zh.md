> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/SetUnionControlNetType/zh.md)

SetUnionControlNetType 节点允许您指定用于条件控制的控制网络类型。该节点接收现有的控制网络，根据您的选择设置其控制类型，从而创建具有指定类型配置的控制网络修改副本。

## 输入参数

| 参数 | 数据类型 | 必填 | 取值范围 | 描述 |
|-----------|-----------|----------|-------|-------------|
| `ControlNet` | CONTROL_NET | 是 | - | 需要设置新类型参数的控制网络 |
| `类型` | STRING | 是 | `"auto"`<br>所有可用的 UNION_CONTROLNET_TYPES 键值 | 要应用的控制网络类型。使用 "auto" 进行自动类型检测，或从可用选项中选择特定的控制网络类型 |

## 输出结果

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `ControlNet` | CONTROL_NET | 应用了指定类型设置的修改后控制网络 |
