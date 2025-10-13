该节点是为了支持阿里巴巴的 Wan Fun Control 模型而添加的，用于视频生成，并在 [此提交](https://github.com/comfyanonymous/ComfyUI/commit/3661c833bcc41b788a7c9f0e7bc48524f8ee5f82) 之后添加。

- **目的：** 准备使用 Wan 2.1 Fun Control 模型进行视频生成所需的条件信息。

WanFunControlToVideo 节点是 ComfyUI 的一个附加功能，旨在支持用于视频生成的 Wan Fun Control 模型，旨在利用 WanFun 控制进行视频创作。

该节点作为准备必要条件信息的起点，并初始化潜在空间的中心点，指导后续使用 Wan 2.1 Fun 模型的视频生成过程。节点的名称清楚地表明了其功能：它接受各种输入并将其转换为适合在 WanFun 框架内控制视频生成的格式。

该节点在 ComfyUI 节点层次结构中的位置表明，它在视频生成管道的早期阶段操作，专注于在实际采样或解码视频帧之前操纵条件信号。

## 输入

| 参数名称           | 必需 | 数据类型           | 描述                                                  | 默认值 |
|:-------------------|:---------|:-------------------|:-------------------------------------------------------------|:-------------|
| positive           | 是      | CONDITIONING       | 标准 ComfyUI 正条件数据，通常来自“CLIP Text Encode”节点。正提示描述用户设想的生成视频的内容、主题和艺术风格。 | N/A  |
| negative           | 是      | CONDITIONING       | 标准 ComfyUI 负条件数据，通常由“CLIP Text Encode”节点生成。负提示指定用户希望在生成视频中避免的元素、风格或伪影。 | N/A  |
| vae                | 是      | VAE                | 需要与 Wan 2.1 Fun 模型系列兼容的 VAE（变分自编码器）模型，用于编码和解码图像/视频数据。 | N/A  |
| width              | 是      | INT                | 输出视频帧的期望宽度（以像素为单位），默认值为 832，最小值为 16，最大值由 nodes.MAX_RESOLUTION 决定，步长为 16。 | 832  |
| height             | 是      | INT                | 输出视频帧的期望高度（以像素为单位），默认值为 480，最小值为 16，最大值由 nodes.MAX_RESOLUTION 决定，步长为 16。 | 480  |
| length             | 是      | INT                | 生成视频中的总帧数，默认值为 81，最小值为 1，最大值由 nodes.MAX_RESOLUTION 决定，步长为 4。 | 81   |
| batch_size         | 是      | INT                | 一次生成的视频数量，默认值为 1，最小值为 1，最大值为 4096。 | 1    |
| clip_vision_output | 否       | CLIP_VISION_OUTPUT | （可选）由 CLIP 视觉模型提取的视觉特征，允许进行视觉风格和内容指导。 | 无 |
| start_image        | 否       | IMAGE              | （可选）影响生成视频开头的初始图像。 | 无 |
| control_video      | 否       | IMAGE              | （可选）允许用户提供经过预处理的 ControlNet 参考视频，以指导生成视频的运动和潜在结构。| 无 |

## 输出

| 参数名称           | 数据类型           | 描述                                                  |
|:-------------------|:-------------------|:-------------------------------------------------------------|
| positive           | CONDITIONING       | 提供增强的正条件数据，包括编码的 start_image 和 control_video。 |
| negative           | CONDITIONING       | 提供同样增强的负条件数据，包含相同的 concat_latent_image。 |
| latent             | LATENT             | 一个字典，包含一个空的潜在张量，键为“samples”。 |
