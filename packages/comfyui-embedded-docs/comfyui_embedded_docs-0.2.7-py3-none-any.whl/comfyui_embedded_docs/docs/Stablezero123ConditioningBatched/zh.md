此节点专为StableZero123模型设计，以批量方式处理条件信息。它专注于同时高效处理多组条件数据，为批量处理至关重要的场景优化工作流程。

## 输入

| 参数名称 | 数据类型 | 作用 |
| --- | --- | --- |
| `clip_vision` | `CLIP_VISION` | 提供条件过程的视觉上下文的CLIP视觉嵌入。 |
| `init_image` | `IMAGE` | 要进行条件处理的初始图像，作为生成过程的起点。 |
| `vae` | `VAE` | 用于条件过程中编码和解码图像的变分自编码器。 |
| `width` | `INT` | 输出图像的宽度。 |
| `height` | `INT` | 输出图像的高度。 |
| `batch_size` | `INT` | 单批次中要处理的条件集数量。 |
| `elevation` | `FLOAT` | 3D模型条件的仰角，影响生成图像的视角。 |
| `azimuth` | `FLOAT` | 3D模型条件的方位角，影响生成图像的方向。 |
| `elevation_batch_increment` | `FLOAT` | 仰角在批量中的增量变化，允许不同的视角。 |
| `azimuth_batch_increment` | `FLOAT` | 方位角在批量中的增量变化，允许不同的方向。 |

## 输出

| 参数名称 | 数据类型 | 作用 |
| --- | --- | --- |
| `positive` | `CONDITIONING` | 正面条件输出，专为促进生成内容中的某些特征或方面而定制。 |
| `negative` | `CONDITIONING` | 负面条件输出，专为降低生成内容中的某些特征或方面而定制。 |
| `latent` | `LATENT` | 来自条件过程的潜在表示，可供进一步处理或生成步骤使用。 |
