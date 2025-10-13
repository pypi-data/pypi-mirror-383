This node is designed for upscaling images using a specified upscale model. It efficiently manages the upscaling process by adjusting the image to the appropriate device, optimizing memory usage, and applying the upscale model in a tiled manner to prevent potential out-of-memory errors.

## Inputs

| Parameter         | Comfy dtype       | Description                                                                 |
|-------------------|-------------------|----------------------------------------------------------------------------|
| `upscale_model`   | `UPSCALE_MODEL`   | The upscale model to be used for upscaling the image. It is crucial for defining the upscaling algorithm and its parameters. |
| `image`           | `IMAGE`           | The image to be upscaled. This input is essential for determining the source content that will undergo the upscaling process. |

## Outputs

| Parameter | Data Type | Description                                        |
|-----------|-------------|----------------------------------------------------|
| `image`   | `IMAGE`     | The upscaled image, processed by the upscale model. This output is the result of the upscaling operation, showcasing the enhanced resolution or quality. |
