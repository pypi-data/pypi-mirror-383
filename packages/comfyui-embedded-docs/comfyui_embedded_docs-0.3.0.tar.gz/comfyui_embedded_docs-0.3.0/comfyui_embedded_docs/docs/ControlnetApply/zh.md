目前文档是原来 `Apply ControlNet(Advanced)`节点的说明，最早的 `Apply ControlNet` 节点已被重命名为 `Apply ControlNet(Old)`，但 comfyui.org 为了保证兼容性，在你下载到的许多工作流文件夹里应该还可以看到 `Apply ControlNet(Old)` 节点，但是目前你已经无法通过搜索或者节点列表看到 `Apply ControlNet(Old)` 节点，所以请使用 `Apply ControlNet` 节点。

此节点将 ControlNet 应用于给定的图像和条件，根据控制网络的参数和指定的强度调整图像的属性，比如 Depth、OpenPose、Canny、HED等等。

使用 controlNet 要求对输入图像进行预处理，由于ComfyUI 初始节点不带处理器和 controlNet 模型，所以请先安装ContrlNet预处理器[这里下载与处理器](https://github.com/Fannovel16/comfy_controlnet_preprocessors)和contrlNet 对应的模型。

## Apply ControlNet 输入类型

| 参数名称 | 数据类型 | 作用 |
| --- | --- | --- |
| `positive` | `CONDITIONING` | 正向条件数据，来自 `CLIP文本编码器`或者其它条件输入|
| `negative` | `CONDITIONING` | 负向条件数据，来自 `CLIP文本编码器`或者其它条件输入|
| `ControlNet` | `CONTROL_NET` | 要应用的controlNet模型，通常输入来自 `controlNt加载器` |
| `图像` | `IMAGE` | 用于 controlNet 应用的图片，需要经过预处理器处理 |
| `vae` | `VAE` | Vae模型输入|
| `强度` | `FLOAT` | 用来控制网络调整的强度，取值0～10。建议取值在0.5～1.5之间比较合理，越小则模型会发挥越高的自由度，越大则会被限制得越严格,过高会出现很诡异的画面。你也可以通过自己测试来调整这个值，用来微调控制网络对图像产生的影响。 |
| `start_percent` | `FLOAT` | 取值 0.000～1.000，确定开始应用controlNet的百分比，比如取值0.2，意味着ControlNet的引导将在扩散过程完成20%时开始影响图像生成|
| `end_percent` | `FLOAT` | 取值 0.000～1.000，确定结束应用controlNet的百分比，比如取值0.8，意味着ControlNet的引导将在扩散过程完成80%时停止影响图像生成|

## Apply ControlNet 输出类型

| 参数名称 | 数据类型 | 作用 |
| --- | --- | --- |
| `positive` | `CONDITIONING` | 经过ControlNet 处理后的正向条件数据，可以输出到下一个ControlNet 或者 K采样器等节点 |
| `negative` | `CONDITIONING` | 经过ControlNet 处理后的负向条件数据，可以输出到下一个ControlNet 或者 K采样器等节点 |

如果要使用**T2IAdaptor样式模型**，请改用`Apply Style Model`节点
