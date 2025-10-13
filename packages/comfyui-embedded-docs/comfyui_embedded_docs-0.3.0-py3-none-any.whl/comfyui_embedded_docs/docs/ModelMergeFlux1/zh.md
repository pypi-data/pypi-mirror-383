> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/ModelMergeFlux1/zh.md)

ModelMergeFlux1 节点通过加权插值的方式融合两个扩散模型的组件，实现模型合并功能。该节点支持对模型不同部分进行细粒度控制，包括图像处理块、时间嵌入层、引导机制、向量输入、文本编码器以及各种变换器块。这使得用户能够基于两个源模型创建具有定制化特征的混合模型。

## 输入参数

| 参数 | 数据类型 | 必填 | 取值范围 | 描述 |
|------|-----------|------|----------|------|
| `模型1` | MODEL | 是 | - | 要合并的第一个源模型 |
| `模型2` | MODEL | 是 | - | 要合并的第二个源模型 |
| `img_in.` | FLOAT | 是 | 0.0 到 1.0 | 图像输入插值权重（默认：1.0） |
| `time_in.` | FLOAT | 是 | 0.0 到 1.0 | 时间嵌入插值权重（默认：1.0） |
| `输入引导` | FLOAT | 是 | 0.0 到 1.0 | 引导机制插值权重（默认：1.0） |
| `vector_in.` | FLOAT | 是 | 0.0 到 1.0 | 向量输入插值权重（默认：1.0） |
| `txt_in.` | FLOAT | 是 | 0.0 到 1.0 | 文本编码器插值权重（默认：1.0） |
| `double_blocks.0.` | FLOAT | 是 | 0.0 到 1.0 | 双块0插值权重（默认：1.0） |
| `double_blocks.1.` | FLOAT | 是 | 0.0 到 1.0 | 双块1插值权重（默认：1.0） |
| `double_blocks.2.` | FLOAT | 是 | 0.0 到 1.0 | 双块2插值权重（默认：1.0） |
| `double_blocks.3.` | FLOAT | 是 | 0.0 到 1.0 | 双块3插值权重（默认：1.0） |
| `double_blocks.4.` | FLOAT | 是 | 0.0 到 1.0 | 双块4插值权重（默认：1.0） |
| `double_blocks.5.` | FLOAT | 是 | 0.0 到 1.0 | 双块5插值权重（默认：1.0） |
| `double_blocks.6.` | FLOAT | 是 | 0.0 到 1.0 | 双块6插值权重（默认：1.0） |
| `double_blocks.7.` | FLOAT | 是 | 0.0 到 1.0 | 双块7插值权重（默认：1.0） |
| `double_blocks.8.` | FLOAT | 是 | 0.0 到 1.0 | 双块8插值权重（默认：1.0） |
| `double_blocks.9.` | FLOAT | 是 | 0.0 到 1.0 | 双块9插值权重（默认：1.0） |
| `double_blocks.10.` | FLOAT | 是 | 0.0 到 1.0 | 双块10插值权重（默认：1.0） |
| `double_blocks.11.` | FLOAT | 是 | 0.0 到 1.0 | 双块11插值权重（默认：1.0） |
| `double_blocks.12.` | FLOAT | 是 | 0.0 到 1.0 | 双块12插值权重（默认：1.0） |
| `double_blocks.13.` | FLOAT | 是 | 0.0 到 1.0 | 双块13插值权重（默认：1.0） |
| `double_blocks.14.` | FLOAT | 是 | 0.0 到 1.0 | 双块14插值权重（默认：1.0） |
| `double_blocks.15.` | FLOAT | 是 | 0.0 到 1.0 | 双块15插值权重（默认：1.0） |
| `double_blocks.16.` | FLOAT | 是 | 0.0 到 1.0 | 双块16插值权重（默认：1.0） |
| `double_blocks.17.` | FLOAT | 是 | 0.0 到 1.0 | 双块17插值权重（默认：1.0） |
| `double_blocks.18.` | FLOAT | 是 | 0.0 到 1.0 | 双块18插值权重（默认：1.0） |
| `single_blocks.0.` | FLOAT | 是 | 0.0 到 1.0 | 单块0插值权重（默认：1.0） |
| `single_blocks.1.` | FLOAT | 是 | 0.0 到 1.0 | 单块1插值权重（默认：1.0） |
| `single_blocks.2.` | FLOAT | 是 | 0.0 到 1.0 | 单块2插值权重（默认：1.0） |
| `single_blocks.3.` | FLOAT | 是 | 0.0 到 1.0 | 单块3插值权重（默认：1.0） |
| `single_blocks.4.` | FLOAT | 是 | 0.0 到 1.0 | 单块4插值权重（默认：1.0） |
| `single_blocks.5.` | FLOAT | 是 | 0.0 到 1.0 | 单块5插值权重（默认：1.0） |
| `single_blocks.6.` | FLOAT | 是 | 0.0 到 1.0 | 单块6插值权重（默认：1.0） |
| `single_blocks.7.` | FLOAT | 是 | 0.0 到 1.0 | 单块7插值权重（默认：1.0） |
| `single_blocks.8.` | FLOAT | 是 | 0.0 到 1.0 | 单块8插值权重（默认：1.0） |
| `single_blocks.9.` | FLOAT | 是 | 0.0 到 1.0 | 单块9插值权重（默认：1.0） |
| `single_blocks.10.` | FLOAT | 是 | 0.0 到 1.0 | 单块10插值权重（默认：1.0） |
| `single_blocks.11.` | FLOAT | 是 | 0.0 到 1.0 | 单块11插值权重（默认：1.0） |
| `single_blocks.12.` | FLOAT | 是 | 0.0 到 1.0 | 单块12插值权重（默认：1.0） |
| `single_blocks.13.` | FLOAT | 是 | 0.0 到 1.0 | 单块13插值权重（默认：1.0） |
| `single_blocks.14.` | FLOAT | 是 | 0.0 到 1.0 | 单块14插值权重（默认：1.0） |
| `single_blocks.15.` | FLOAT | 是 | 0.0 到 1.0 | 单块15插值权重（默认：1.0） |
| `single_blocks.16.` | FLOAT | 是 | 0.0 到 1.0 | 单块16插值权重（默认：1.0） |
| `single_blocks.17.` | FLOAT | 是 | 0.0 到 1.0 | 单块17插值权重（默认：1.0） |
| `single_blocks.18.` | FLOAT | 是 | 0.0 到 1.0 | 单块18插值权重（默认：1.0） |
| `single_blocks.19.` | FLOAT | 是 | 0.0 到 1.0 | 单块19插值权重（默认：1.0） |
| `single_blocks.20.` | FLOAT | 是 | 0.0 到 1.0 | 单块20插值权重（默认：1.0） |
| `single_blocks.21.` | FLOAT | 是 | 0.0 到 1.0 | 单块21插值权重（默认：1.0） |
| `single_blocks.22.` | FLOAT | 是 | 0.0 到 1.0 | 单块22插值权重（默认：1.0） |
| `single_blocks.23.` | FLOAT | 是 | 0.0 到 1.0 | 单块23插值权重（默认：1.0） |
| `single_blocks.24.` | FLOAT | 是 | 0.0 到 1.0 | 单块24插值权重（默认：1.0） |
| `single_blocks.25.` | FLOAT | 是 | 0.0 到 1.0 | 单块25插值权重（默认：1.0） |
| `single_blocks.26.` | FLOAT | 是 | 0.0 到 1.0 | 单块26插值权重（默认：1.0） |
| `single_blocks.27.` | FLOAT | 是 | 0.0 到 1.0 | 单块27插值权重（默认：1.0） |
| `single_blocks.28.` | FLOAT | 是 | 0.0 到 1.0 | 单块28插值权重（默认：1.0） |
| `single_blocks.29.` | FLOAT | 是 | 0.0 到 1.0 | 单块29插值权重（默认：1.0） |
| `single_blocks.30.` | FLOAT | 是 | 0.0 到 1.0 | 单块30插值权重（默认：1.0） |
| `single_blocks.31.` | FLOAT | 是 | 0.0 到 1.0 | 单块31插值权重（默认：1.0） |
| `single_blocks.32.` | FLOAT | 是 | 0.0 到 1.0 | 单块32插值权重（默认：1.0） |
| `single_blocks.33.` | FLOAT | 是 | 0.0 到 1.0 | 单块33插值权重（默认：1.0） |
| `single_blocks.34.` | FLOAT | 是 | 0.0 到 1.0 | 单块34插值权重（默认：1.0） |
| `single_blocks.35.` | FLOAT | 是 | 0.0 到 1.0 | 单块35插值权重（默认：1.0） |
| `single_blocks.36.` | FLOAT | 是 | 0.0 到 1.0 | 单块36插值权重（默认：1.0） |
| `single_blocks.37.` | FLOAT | 是 | 0.0 到 1.0 | 单块37插值权重（默认：1.0） |
| `final_layer.` | FLOAT | 是 | 0.0 到 1.0 | 最终层插值权重（默认：1.0） |

## 输出结果

| 输出名称 | 数据类型 | 描述 |
|----------|-----------|------|
| `model` | MODEL | 融合了两个输入模型特征的合并模型 |
